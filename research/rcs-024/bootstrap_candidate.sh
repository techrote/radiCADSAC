#!/usr/bin/env bash
set -euo pipefail

EXPECTED_COMMIT="3d097a0328e71b826377d4814ab05ec3c3d23871"
EXPECTED_VERSION_COMPLETE="8.1.0"
EXPECTED_VERSION_DEVELOPMENT="dev1"
EXPECTED_VERSION_EXT="${EXPECTED_VERSION_COMPLETE}.${EXPECTED_VERSION_DEVELOPMENT}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPS_ROOT="${RCS024_DEPS_ROOT:-${REPO_ROOT}/.deps/rcs024}"
SOURCE_DIR="${DEPS_ROOT}/occt-src"
BUILD_DIR="${DEPS_ROOT}/occt-build"
INSTALL_DIR="${RCS024_OCCT_PREFIX:-${DEPS_ROOT}/occt-8.1.0-dev1}"
JOBS="${RCS024_BUILD_JOBS:-2}"

REQUIRED_TOOLKITS=(TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo TKPrim TKBO TKShHealing TKDE TKXSBase TKDESTEP)
ADDITIONAL_TOOLKITS="TKernel;TKMath;TKG2d;TKG3d;TKGeomBase;TKBRep;TKGeomAlgo;TKTopAlgo;TKPrim;TKBO;TKShHealing;TKDE;TKXSBase;TKDESTEP"

install_is_usable() {
  [[ -f "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx" ]] || return 1
  local version_header="${INSTALL_DIR}/include/opencascade/Standard_Version.hxx"
  grep -Fq "#define OCC_VERSION_COMPLETE \"${EXPECTED_VERSION_COMPLETE}\"" "${version_header}" || return 1
  grep -Fq "#define OCC_VERSION_DEVELOPMENT \"${EXPECTED_VERSION_DEVELOPMENT}\"" "${version_header}" || return 1
  [[ -f "${INSTALL_DIR}/include/opencascade/BRepGraph.hxx" ]] || return 1
  local toolkit libdir found
  for toolkit in "${REQUIRED_TOOLKITS[@]}"; do
    found=0
    for libdir in lib lib64; do
      if compgen -G "${INSTALL_DIR}/${libdir}/lib${toolkit}.so*" >/dev/null; then found=1; break; fi
    done
    [[ "${found}" -eq 1 ]] || return 1
  done
}

if install_is_usable; then
  echo "RCS-024 candidate already installed at ${INSTALL_DIR}"
  exit 0
fi
rm -rf "${INSTALL_DIR}"
mkdir -p "${DEPS_ROOT}"
if [[ ! -d "${SOURCE_DIR}/.git" ]]; then
  rm -rf "${SOURCE_DIR}"
  git clone --filter=blob:none --no-checkout https://github.com/Open-Cascade-SAS/OCCT.git "${SOURCE_DIR}"
fi
git -C "${SOURCE_DIR}" fetch --depth=1 origin "${EXPECTED_COMMIT}"
git -C "${SOURCE_DIR}" checkout --detach "${EXPECTED_COMMIT}"
[[ "$(git -C "${SOURCE_DIR}" rev-parse HEAD)" == "${EXPECTED_COMMIT}" ]]

rm -rf "${BUILD_DIR}"
cmake -S "${SOURCE_DIR}" -B "${BUILD_DIR}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
  -DBUILD_CPP_STANDARD=C++17 -DBUILD_LIBRARY_TYPE=Shared \
  -DBUILD_MODULE_FoundationClasses=OFF -DBUILD_MODULE_ModelingData=OFF \
  -DBUILD_MODULE_ModelingAlgorithms=OFF -DBUILD_MODULE_ApplicationFramework=OFF \
  -DBUILD_MODULE_DataExchange=OFF -DBUILD_MODULE_Visualization=OFF -DBUILD_MODULE_Draw=OFF \
  "-DBUILD_ADDITIONAL_TOOLKITS=${ADDITIONAL_TOOLKITS}" \
  -DUSE_TCL=OFF -DUSE_TK=OFF -DUSE_FREETYPE=OFF -DUSE_FREEIMAGE=OFF -DUSE_TBB=OFF \
  -DUSE_VTK=OFF -DUSE_OPENVR=OFF -DUSE_RAPIDJSON=OFF -DUSE_DRACO=OFF -DUSE_FFMPEG=OFF \
  -DUSE_EIGEN=OFF -DUSE_OPENGL=OFF -DUSE_XLIB=OFF
cmake --build "${BUILD_DIR}" --parallel "${JOBS}"
cmake --install "${BUILD_DIR}"
install_is_usable
cat > "${INSTALL_DIR}/RCS024_SOURCE_PIN.txt" <<EOF
repository=https://github.com/Open-Cascade-SAS/OCCT.git
commit=${EXPECTED_COMMIT}
version=${EXPECTED_VERSION_EXT}
version_complete=${EXPECTED_VERSION_COMPLETE}
version_development=${EXPECTED_VERSION_DEVELOPMENT}
build_profile=release-shared-cxx17-worker-only-headless-v4-compatible
selected_toolkits=${ADDITIONAL_TOOLKITS}
EOF
