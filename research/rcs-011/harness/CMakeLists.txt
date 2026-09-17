cmake_minimum_required(VERSION 3.20)
project(rcs011_mill_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

set(RCS011_OCCT_ROOT "" CACHE PATH "Pinned OCCT installation root")
if(NOT RCS011_OCCT_ROOT AND DEFINED ENV{RCS006_OCCT_PREFIX})
  set(RCS011_OCCT_ROOT "$ENV{RCS006_OCCT_PREFIX}")
endif()
if(NOT RCS011_OCCT_ROOT AND CMAKE_PREFIX_PATH)
  list(GET CMAKE_PREFIX_PATH 0 RCS011_OCCT_ROOT)
endif()
if(NOT RCS011_OCCT_ROOT)
  message(FATAL_ERROR "Set RCS011_OCCT_ROOT or RCS006_OCCT_PREFIX to the pinned OCCT install")
endif()

find_path(RCS011_OCCT_INCLUDE_DIR
  NAMES Standard.hxx
  PATHS "${RCS011_OCCT_ROOT}/include/opencascade"
  NO_DEFAULT_PATH
  REQUIRED)

set(RCS011_OCCT_TOOLKITS
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

set(RCS011_OCCT_LIBRARIES "")
foreach(toolkit IN LISTS RCS011_OCCT_TOOLKITS)
  find_library(RCS011_${toolkit}_LIBRARY
    NAMES ${toolkit}
    PATHS "${RCS011_OCCT_ROOT}/lib" "${RCS011_OCCT_ROOT}/lib64"
    NO_DEFAULT_PATH
    REQUIRED)
  list(APPEND RCS011_OCCT_LIBRARIES "${RCS011_${toolkit}_LIBRARY}")
endforeach()

add_executable(rcs011_mill_worker mill_worker.cpp)
target_include_directories(rcs011_mill_worker PRIVATE "${RCS011_OCCT_INCLUDE_DIR}")
target_link_libraries(rcs011_mill_worker PRIVATE
  ${RCS011_OCCT_LIBRARIES}
  Threads::Threads
)

if(MSVC)
  target_compile_options(rcs011_mill_worker PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs011_mill_worker PRIVATE -Wall -Wextra -Wpedantic)
endif()
