cmake_minimum_required(VERSION 3.20)
project(rcs010_lathe_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

set(RCS010_OCCT_ROOT "" CACHE PATH "Pinned OCCT installation root")
if(NOT RCS010_OCCT_ROOT AND DEFINED ENV{RCS006_OCCT_PREFIX})
  set(RCS010_OCCT_ROOT "$ENV{RCS006_OCCT_PREFIX}")
endif()
if(NOT RCS010_OCCT_ROOT AND CMAKE_PREFIX_PATH)
  list(GET CMAKE_PREFIX_PATH 0 RCS010_OCCT_ROOT)
endif()
if(NOT RCS010_OCCT_ROOT)
  message(FATAL_ERROR "Set RCS010_OCCT_ROOT or RCS006_OCCT_PREFIX to the pinned OCCT install")
endif()

find_path(RCS010_OCCT_INCLUDE_DIR
  NAMES Standard.hxx
  PATHS "${RCS010_OCCT_ROOT}/include/opencascade"
  NO_DEFAULT_PATH
  REQUIRED)

set(RCS010_OCCT_TOOLKITS
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

set(RCS010_OCCT_LIBRARIES "")
foreach(toolkit IN LISTS RCS010_OCCT_TOOLKITS)
  find_library(RCS010_${toolkit}_LIBRARY
    NAMES ${toolkit}
    PATHS "${RCS010_OCCT_ROOT}/lib" "${RCS010_OCCT_ROOT}/lib64"
    NO_DEFAULT_PATH
    REQUIRED)
  list(APPEND RCS010_OCCT_LIBRARIES "${RCS010_${toolkit}_LIBRARY}")
endforeach()

add_executable(rcs010_lathe_worker lathe_worker.cpp)
target_include_directories(rcs010_lathe_worker PRIVATE "${RCS010_OCCT_INCLUDE_DIR}")
target_link_libraries(rcs010_lathe_worker PRIVATE
  ${RCS010_OCCT_LIBRARIES}
  Threads::Threads
)

if(MSVC)
  target_compile_options(rcs010_lathe_worker PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs010_lathe_worker PRIVATE -Wall -Wextra -Wpedantic)
endif()
