#!/usr/bin/env bash
set -euo pipefail

EXPECTED_COMMIT="b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_VERSION="8.0.1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DEPS_ROOT="${RCS006_DEPS_ROOT:-${REPO_ROOT}/.deps/rcs006}"
SOURCE_DIR="${DEPS_ROOT}/occt-src"
BUILD_DIR="${DEPS_ROOT}/occt-build"
INSTALL_DIR="${RCS006_OCCT_PREFIX:-${DEPS_ROOT}/occt-${EXPECTED_VERSION}}"
JOBS="${RCS006_BUILD_JOBS:-1}"

# These are the toolkits the worker links directly plus the disabled-module
# toolkit targets referenced by OCCT's installed DataExchange CMake exports.
# BUILD_ADDITIONAL_TOOLKITS builds transitive dependencies, but dependencies
# belonging to otherwise-disabled modules are not necessarily installed/exported
# unless they are selected explicitly. An install missing any of these targets
# makes find_package(OpenCASCADE ... DataExchange) reject an otherwise valid
# 8.0.1 installation.
REQUIRED_TOOLKITS=(
  TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo TKPrim
  TKBO TKShHealing TKDE TKXSBase TKDESTEP
  TKCAF TKCDF TKLCAF TKService TKV3d TKVCAF
)
ADDITIONAL_TOOLKITS="TKBO;TKDESTEP;TKCAF;TKCDF;TKLCAF;TKService;TKV3d;TKVCAF"

install_is_usable() {
  [[ -f "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx" ]] || return 1
  grep -q "#define OCC_VERSION_COMPLETE \"${EXPECTED_VERSION}\"" \
    "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx" || return 1
  [[ -f "${INSTALL_DIR}/lib/cmake/opencascade/OpenCASCADEConfig.cmake" ]] || return 1

  local toolkit libdir found
  for toolkit in "${REQUIRED_TOOLKITS[@]}"; do
    found=0
    for libdir in lib lib64; do
      if compgen -G "${INSTALL_DIR}/${libdir}/lib${toolkit}.so*" >/dev/null; then
        found=1
        break
      fi
    done
    if [[ "${found}" -ne 1 ]]; then
      echo "OCCT install is missing required toolkit ${toolkit}" >&2
      return 1
    fi
  done
  return 0
}

if install_is_usable; then
  echo "RCS-006 OCCT already installed at ${INSTALL_DIR}"
  echo "RCS006_OCCT_PREFIX=${INSTALL_DIR}"
  exit 0
fi
if [[ -d "${INSTALL_DIR}" ]]; then
  echo "Existing OCCT install is incomplete or has an unexpected version; rebuilding" >&2
  rm -rf "${INSTALL_DIR}"
fi

mkdir -p "${DEPS_ROOT}"
if [[ ! -d "${SOURCE_DIR}/.git" ]]; then
  rm -rf "${SOURCE_DIR}"
  git clone --filter=blob:none --no-checkout https://github.com/Open-Cascade-SAS/OCCT.git "${SOURCE_DIR}"
fi

git -C "${SOURCE_DIR}" fetch --depth=1 origin "${EXPECTED_COMMIT}"
git -C "${SOURCE_DIR}" checkout --detach "${EXPECTED_COMMIT}"
ACTUAL_COMMIT="$(git -C "${SOURCE_DIR}" rev-parse HEAD)"
if [[ "${ACTUAL_COMMIT}" != "${EXPECTED_COMMIT}" ]]; then
  echo "OCCT source pin mismatch: ${ACTUAL_COMMIT}" >&2
  exit 2
fi

# Keep broad modules disabled and select only the Boolean/STEP worker toolkits
# plus the package-export dependencies identified above. This preserves the
# headless minimal build while producing a self-consistent installed CMake
# package. Disable Xlib/OpenGL explicitly because TKService/TKV3d are required
# as package dependencies but the research worker does not render anything.
rm -rf "${BUILD_DIR}"
cmake -S "${SOURCE_DIR}" -B "${BUILD_DIR}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
  -DBUILD_CPP_STANDARD=C++17 \
  -DBUILD_LIBRARY_TYPE=Shared \
  -DBUILD_MODULE_FoundationClasses=OFF \
  -DBUILD_MODULE_ModelingData=OFF \
  -DBUILD_MODULE_ModelingAlgorithms=OFF \
  -DBUILD_MODULE_ApplicationFramework=OFF \
  -DBUILD_MODULE_DataExchange=OFF \
  -DBUILD_MODULE_Visualization=OFF \
  -DBUILD_MODULE_Draw=OFF \
  "-DBUILD_ADDITIONAL_TOOLKITS=${ADDITIONAL_TOOLKITS}" \
  -DUSE_TCL=OFF \
  -DUSE_TK=OFF \
  -DUSE_FREETYPE=OFF \
  -DUSE_FREEIMAGE=OFF \
  -DUSE_TBB=OFF \
  -DUSE_VTK=OFF \
  -DUSE_OPENVR=OFF \
  -DUSE_RAPIDJSON=OFF \
  -DUSE_DRACO=OFF \
  -DUSE_FFMPEG=OFF \
  -DUSE_EIGEN=OFF \
  -DUSE_OPENGL=OFF \
  -DUSE_XLIB=OFF

cmake --build "${BUILD_DIR}" --parallel "${JOBS}"
cmake --install "${BUILD_DIR}"

if ! install_is_usable; then
  echo "OCCT installation is incomplete or is not ${EXPECTED_VERSION}" >&2
  exit 3
fi

cat > "${INSTALL_DIR}/RCS006_SOURCE_PIN.txt" <<EOF
repository=https://github.com/Open-Cascade-SAS/OCCT.git
commit=${EXPECTED_COMMIT}
version=${EXPECTED_VERSION}
build_profile=release-shared-cxx17-minimal-headless-v3
selected_toolkits=${ADDITIONAL_TOOLKITS}
xlib=off
opengl=off
EOF

echo "RCS006_OCCT_PREFIX=${INSTALL_DIR}"
