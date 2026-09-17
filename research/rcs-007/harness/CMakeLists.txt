cmake_minimum_required(VERSION 3.20)
project(rcs007_finish_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

set(RCS007_OCCT_ROOT "" CACHE PATH "Pinned OCCT installation root")
if(NOT RCS007_OCCT_ROOT AND DEFINED ENV{RCS006_OCCT_PREFIX})
  set(RCS007_OCCT_ROOT "$ENV{RCS006_OCCT_PREFIX}")
endif()
if(NOT RCS007_OCCT_ROOT AND CMAKE_PREFIX_PATH)
  list(GET CMAKE_PREFIX_PATH 0 RCS007_OCCT_ROOT)
endif()
if(NOT RCS007_OCCT_ROOT)
  message(FATAL_ERROR "Set RCS007_OCCT_ROOT or RCS006_OCCT_PREFIX to the pinned OCCT install")
endif()

find_path(RCS007_OCCT_INCLUDE_DIR
  NAMES Standard.hxx
  PATHS "${RCS007_OCCT_ROOT}/include/opencascade"
  NO_DEFAULT_PATH
  REQUIRED)

set(RCS007_OCCT_TOOLKITS
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
)

set(RCS007_OCCT_LIBRARIES "")
foreach(toolkit IN LISTS RCS007_OCCT_TOOLKITS)
  find_library(RCS007_${toolkit}_LIBRARY
    NAMES ${toolkit}
    PATHS "${RCS007_OCCT_ROOT}/lib" "${RCS007_OCCT_ROOT}/lib64"
    NO_DEFAULT_PATH
    REQUIRED)
  list(APPEND RCS007_OCCT_LIBRARIES "${RCS007_${toolkit}_LIBRARY}")
endforeach()

add_executable(rcs007_finish_worker repeated_finish_worker.cpp)
target_include_directories(rcs007_finish_worker PRIVATE "${RCS007_OCCT_INCLUDE_DIR}")
target_link_libraries(rcs007_finish_worker PRIVATE
  ${RCS007_OCCT_LIBRARIES}
  Threads::Threads
)

if(MSVC)
  target_compile_options(rcs007_finish_worker PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs007_finish_worker PRIVATE -Wall -Wextra -Wpedantic)
endif()
