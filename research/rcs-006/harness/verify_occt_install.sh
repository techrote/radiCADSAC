#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPOSITORY="https://github.com/Open-Cascade-SAS/OCCT.git"
EXPECTED_COMMIT="b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_VERSION="8.0.1"
EXPECTED_BUILD_PROFILE="release-shared-cxx17-minimal-headless-v3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
INSTALL_DIR="${RCS006_OCCT_PREFIX:-${REPO_ROOT}/.deps/rcs006/occt-${EXPECTED_VERSION}}"
PIN_FILE="${INSTALL_DIR}/RCS006_SOURCE_PIN.txt"
VERSION_HEADER="${INSTALL_DIR}/include/opencascade/Standard_Version.hxx"
CONFIG_FILE="${INSTALL_DIR}/lib/cmake/opencascade/OpenCASCADEConfig.cmake"

REQUIRED_TOOLKITS=(
  TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo TKPrim
  TKBO TKShHealing TKDE TKXSBase TKDESTEP
  TKCAF TKCDF TKLCAF TKService TKV3d TKVCAF
)

fail() {
  echo "RCS-006 OCCT install verification failed: $*" >&2
  exit 1
}

[[ -f "${VERSION_HEADER}" ]] || fail "missing Standard_Version.hxx"
grep -Fq "#define OCC_VERSION_COMPLETE \"${EXPECTED_VERSION}\"" "${VERSION_HEADER}" \
  || fail "version header does not report ${EXPECTED_VERSION}"
[[ -f "${CONFIG_FILE}" ]] || fail "missing installed OpenCASCADEConfig.cmake"
[[ -f "${PIN_FILE}" ]] || fail "missing RCS006_SOURCE_PIN.txt"

grep -Fxq "repository=${EXPECTED_REPOSITORY}" "${PIN_FILE}" || fail "source repository pin mismatch"
grep -Fxq "commit=${EXPECTED_COMMIT}" "${PIN_FILE}" || fail "source commit pin mismatch"
grep -Fxq "version=${EXPECTED_VERSION}" "${PIN_FILE}" || fail "source version pin mismatch"
grep -Fxq "build_profile=${EXPECTED_BUILD_PROFILE}" "${PIN_FILE}" || fail "build profile mismatch"
grep -Fxq "xlib=off" "${PIN_FILE}" || fail "Xlib must be disabled"
grep -Fxq "opengl=off" "${PIN_FILE}" || fail "OpenGL must be disabled"

for toolkit in "${REQUIRED_TOOLKITS[@]}"; do
  found=0
  for libdir in lib lib64; do
    if compgen -G "${INSTALL_DIR}/${libdir}/lib${toolkit}.so*" >/dev/null; then
      found=1
      break
    fi
  done
  [[ "${found}" -eq 1 ]] || fail "missing required toolkit ${toolkit}"
done

echo "RCS-006 OCCT install verified"
echo "  prefix=${INSTALL_DIR}"
echo "  version=${EXPECTED_VERSION}"
echo "  commit=${EXPECTED_COMMIT}"
echo "  required_toolkits=${#REQUIRED_TOOLKITS[@]}"
