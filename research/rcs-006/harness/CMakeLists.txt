cmake_minimum_required(VERSION 3.20)
project(rcs006_occt_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenCASCADE CONFIG REQUIRED COMPONENTS FoundationClasses ModelingData ModelingAlgorithms DataExchange)

add_executable(rcs006_occt_worker occt_worker.cpp)
target_include_directories(rcs006_occt_worker PRIVATE ${OpenCASCADE_INCLUDE_DIR})
target_link_libraries(rcs006_occt_worker PRIVATE
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

if(MSVC)
  target_compile_options(rcs006_occt_worker PRIVATE /W4 /permissive-)
else()
  target_compile_options(rcs006_occt_worker PRIVATE -Wall -Wextra -Wpedantic)
endif()
