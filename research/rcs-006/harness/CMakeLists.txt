cmake_minimum_required(VERSION 3.20)
project(rcs006_occt_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

# The pinned minimal OCCT install intentionally omits unrelated application /
# visualization packages. OCCT's installed DataExchange package metadata still
# references some of those disabled targets, so find_package(OpenCASCADE ...)
# rejects an otherwise complete worker install. Resolve the exact worker ABI
# surface instead: one public include tree plus only the toolkits linked below.
# This also keeps the benchmark adapter honest about its actual dependencies.
set(RCS006_OCCT_ROOT "" CACHE PATH "Pinned OCCT installation root")
if(NOT RCS006_OCCT_ROOT AND DEFINED ENV{RCS006_OCCT_PREFIX})
  set(RCS006_OCCT_ROOT "$ENV{RCS006_OCCT_PREFIX}")
endif()
if(NOT RCS006_OCCT_ROOT AND CMAKE_PREFIX_PATH)
  list(GET CMAKE_PREFIX_PATH 0 RCS006_OCCT_ROOT)
endif()
if(NOT RCS006_OCCT_ROOT)
  message(FATAL_ERROR "Set RCS006_OCCT_ROOT or RCS006_OCCT_PREFIX to the pinned OCCT install")
endif()

find_path(RCS006_OCCT_INCLUDE_DIR
  NAMES Standard.hxx
  PATHS "${RCS006_OCCT_ROOT}/include/opencascade"
  NO_DEFAULT_PATH
  REQUIRED)

set(RCS006_OCCT_TOOLKITS
  TKernel
  TKMath
  TKG2d
  TKG3d
  TKGeomBase
  TKBRep
  TKGeomAlgo
  TKTopAlgo
  TKPrim
  TKBO
  TKShHealing
  TKDE
  TKXSBase
  TKDESTEP
)

set(RCS006_OCCT_LIBRARIES "")
foreach(toolkit IN LISTS RCS006_OCCT_TOOLKITS)
  find_library(RCS006_${toolkit}_LIBRARY
    NAMES ${toolkit}
    PATHS "${RCS006_OCCT_ROOT}/lib" "${RCS006_OCCT_ROOT}/lib64"
    NO_DEFAULT_PATH
    REQUIRED)
  list(APPEND RCS006_OCCT_LIBRARIES "${RCS006_${toolkit}_LIBRARY}")
endforeach()

add_executable(rcs006_occt_worker occt_worker.cpp)
target_include_directories(rcs006_occt_worker PRIVATE "${RCS006_OCCT_INCLUDE_DIR}")
target_link_libraries(rcs006_occt_worker PRIVATE
  ${RCS006_OCCT_LIBRARIES}
  Threads::Threads
)

if(MSVC)
  target_compile_options(rcs006_occt_worker PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs006_occt_worker PRIVATE -Wall -Wextra -Wpedantic)
endif()
