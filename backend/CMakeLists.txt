cmake_minimum_required(VERSION 3.10)
project(Backend)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -ggdb")

include(cmake/CPM.cmake)

CPMAddPackage("gh:nlohmann/json@3.12.0")
CPMAddPackage("gh:redis/hiredis@1.3.0")
set(JWT_BUILD_EXAMPLES off CACHE BOOL "Build the examples" FORCE)
CPMAddPackage("gh:Thalhammer/jwt-cpp@0.7.1")
set(TOM off CACHE BOOL "Disabels tom" FORCE)
CPMAddPackage("gh:silverqx/TinyORM@0.38.1")

find_package(Boost REQUIRED COMPONENTS system filesystem url program_options)
find_package(OpenSSL REQUIRED)

include_directories(${Boost_INCLUDE_DIRS} ${CMAKE_SOURCE_DIR}/include nlohmann_json::nlohmann_json hiredis::hiredis jwt-cpp TinyOrm::TinyOrm)

add_executable(api
  ${CMAKE_SOURCE_DIR}/src/config.cpp
  ${CMAKE_SOURCE_DIR}/src/main.cpp
  ${CMAKE_SOURCE_DIR}/src/router.cpp
  ${CMAKE_SOURCE_DIR}/src/version.cpp
)
target_link_libraries(api PRIVATE ${Boost_LIBRARIES} nlohmann_json::nlohmann_json hiredis::hiredis jwt-cpp pthread argon2 OpenSSL::Crypto OpenSSL::SSL TinyOrm::TinyOrm)
execute_process(COMMAND git rev-parse --short HEAD OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE GIT_COMMIT_HASH)
message(STATUS "Git commit hash: ${GIT_COMMIT_HASH}")
target_compile_definitions(api PRIVATE GIT_SHASH="${GIT_COMMIT_HASH}")