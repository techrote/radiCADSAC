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
JOBS="${RCS006_BUILD_JOBS:-2}"

if [[ -f "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx" ]]; then
  if grep -q "#define OCC_VERSION_COMPLETE \"${EXPECTED_VERSION}\"" "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx"; then
    echo "RCS-006 OCCT already installed at ${INSTALL_DIR}"
    echo "RCS006_OCCT_PREFIX=${INSTALL_DIR}"
    exit 0
  fi
  echo "Existing OCCT install has unexpected version; rebuilding" >&2
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

rm -rf "${BUILD_DIR}"
cmake -S "${SOURCE_DIR}" -B "${BUILD_DIR}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
  -DBUILD_CPP_STANDARD=C++17 \
  -DBUILD_LIBRARY_TYPE=Shared \
  -DBUILD_MODULE_FoundationClasses=ON \
  -DBUILD_MODULE_ModelingData=ON \
  -DBUILD_MODULE_ModelingAlgorithms=ON \
  -DBUILD_MODULE_ApplicationFramework=ON \
  -DBUILD_MODULE_DataExchange=ON \
  -DBUILD_MODULE_Visualization=OFF \
  -DBUILD_MODULE_Draw=OFF \
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
  -DUSE_OPENGL=OFF

cmake --build "${BUILD_DIR}" --parallel "${JOBS}"
cmake --install "${BUILD_DIR}"

if [[ ! -f "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx" ]]; then
  echo "OCCT installation did not produce Standard_Version.hxx" >&2
  exit 3
fi
if ! grep -q "#define OCC_VERSION_COMPLETE \"${EXPECTED_VERSION}\"" "${INSTALL_DIR}/include/opencascade/Standard_Version.hxx"; then
  echo "OCCT installed version is not ${EXPECTED_VERSION}" >&2
  exit 4
fi

cat > "${INSTALL_DIR}/RCS006_SOURCE_PIN.txt" <<EOF
repository=https://github.com/Open-Cascade-SAS/OCCT.git
commit=${EXPECTED_COMMIT}
version=${EXPECTED_VERSION}
build_profile=release-shared-cxx17-minimal-v1
EOF

echo "RCS006_OCCT_PREFIX=${INSTALL_DIR}"
