cmake_minimum_required(VERSION 3.20)
project(rcs026_toolchain_probe LANGUAGES CXX)

add_executable(rcs026_toolchain_probe toolchain_probe.cpp)
target_compile_features(rcs026_toolchain_probe PRIVATE cxx_std_17)
set_target_properties(rcs026_toolchain_probe PROPERTIES CXX_EXTENSIONS OFF)
if(MSVC)
  # MSVC otherwise reports the legacy 199711L __cplusplus value even while
  # compiling in C++17 mode; make the probe report the actual language mode.
  target_compile_options(rcs026_toolchain_probe PRIVATE /Zc:__cplusplus)
endif()

enable_testing()
add_test(
  NAME rcs026-toolchain-probe
  COMMAND rcs026_toolchain_probe "${CMAKE_BINARY_DIR}/toolchain.json" "${CMAKE_GENERATOR}"
)
