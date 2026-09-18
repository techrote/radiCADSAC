cmake_minimum_required(VERSION 3.20)
project(rcs022_step_worker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCASCADE 8.0.1 REQUIRED COMPONENTS
  FoundationClasses
  ModelingData
  ModelingAlgorithms
  DataExchange
)

add_executable(rcs022_step_worker step_worker.cpp)
target_include_directories(rcs022_step_worker PRIVATE ${OpenCASCADE_INCLUDE_DIR})
target_link_libraries(rcs022_step_worker PRIVATE
  TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo TKPrim TKBO
  TKShHealing TKDE TKXSBase TKDESTEP
)
