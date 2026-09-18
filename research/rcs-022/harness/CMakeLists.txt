cmake_minimum_required(VERSION 3.20)
project(rcs022_step_exporter LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(RCS022_OCCT_ROOT "" CACHE PATH "Pinned OCCT installation root")
if(NOT RCS022_OCCT_ROOT AND DEFINED ENV{RCS006_OCCT_PREFIX})
  set(RCS022_OCCT_ROOT "$ENV{RCS006_OCCT_PREFIX}")
endif()
if(NOT RCS022_OCCT_ROOT AND CMAKE_PREFIX_PATH)
  list(GET CMAKE_PREFIX_PATH 0 RCS022_OCCT_ROOT)
endif()
if(NOT RCS022_OCCT_ROOT)
  message(FATAL_ERROR "Set RCS022_OCCT_ROOT or RCS006_OCCT_PREFIX to the pinned OCCT install")
endif()

find_path(RCS022_OCCT_INCLUDE_DIR NAMES Standard.hxx
  PATHS "${RCS022_OCCT_ROOT}/include/opencascade" NO_DEFAULT_PATH REQUIRED)

set(RCS022_OCCT_TOOLKITS
  TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo
  TKPrim TKBO TKShHealing TKDE TKXSBase TKDESTEP)
set(RCS022_OCCT_LIBRARIES "")
foreach(toolkit IN LISTS RCS022_OCCT_TOOLKITS)
  find_library(RCS022_${toolkit}_LIBRARY NAMES ${toolkit}
    PATHS "${RCS022_OCCT_ROOT}/lib" "${RCS022_OCCT_ROOT}/lib64"
    NO_DEFAULT_PATH REQUIRED)
  list(APPEND RCS022_OCCT_LIBRARIES "${RCS022_${toolkit}_LIBRARY}")
endforeach()

add_executable(rcs022_step_exporter step_exporter.cpp)
target_include_directories(rcs022_step_exporter PRIVATE "${RCS022_OCCT_INCLUDE_DIR}")
target_link_libraries(rcs022_step_exporter PRIVATE ${RCS022_OCCT_LIBRARIES})

if(MSVC)
  target_compile_options(rcs022_step_exporter PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs022_step_exporter PRIVATE -Wall -Wextra -Wpedantic)
endif()
