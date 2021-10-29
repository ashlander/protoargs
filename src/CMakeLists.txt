# Project
cmake_minimum_required(VERSION 2.6)
project (Protoargs)

# with conan
#option(WITH_CONAN "Switch conan build" ON)
if (WITH_CONAN)
    message(STATUS "CONAN BUILD enabled")
else()
    message(STATUS "CONAN BUILD disabled")
endif()

if (WITH_CONAN)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
else()
endif()

# Compiler options
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++17" COMPILER_SUPPORTS_CXX17)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX17)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
#elseif(COMPILER_SUPPORTS_CXX14) # disabling it becuse of issue with clang v3.5 and code coverage https://github.com/philsquared/Catch/issues/686
#    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
elseif(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

# treat warnings as errors
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror")

# remove some warnings
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-comment")

# define new __FILENAME__, which is shorter than __FILE__ 
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D__FILENAME__='\"$(subst ${CMAKE_SOURCE_DIR}/,,$(abspath $<))\"'")

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")

# The version number.
set (${PROJECT_NAME}_VERSION_MAJOR 0)
set (${PROJECT_NAME}_VERSION_MINOR 1)

set(CMAKE_BINARY_LIBS ${CMAKE_SOURCE_DIR}/libs)

if (NOT WITH_CONAN)
    set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)
    set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/libs)
endif()

set(PROJECT_INCLUDE_DIR     ${PROJECT_SOURCE_DIR}/include)  # BUILD include
set(PROJECT_INCLUDEX_DIR    ${PROJECT_SOURCE_DIR}/includex) # EXPORT only include

# get build number
if (NOT "$ENV{CI_PIPELINE_ID}" STREQUAL "")
   set(BUILD_NUM "$ENV{CI_PIPELINE_ID}" CACHE INTERNAL "Build number from gitlab pipe")
else()
   set(BUILD_NUM "0")
endif()

# get git hash
if (NOT "$ENV{CI_COMMIT_SHORT_SHA}" STREQUAL "")
   set(GIT_HASH "$ENV{CI_COMMIT_SHORT_SHA}" CACHE INTERNAL "Hash from git")
else()
    find_program( GIT_PATH git )
    if(GIT_PATH)
       set(GIT_MODIFIED_COMMAND bash "-c" "${GIT_PATH} status | grep modified | wc -l")
       execute_process(COMMAND ${GIT_MODIFIED_COMMAND} OUTPUT_VARIABLE GIT_MODIFIED)
       string(STRIP ${GIT_MODIFIED} GIT_MODIFIED)
       execute_process(COMMAND ${GIT_PATH}  rev-parse --short HEAD OUTPUT_VARIABLE GIT_HASH)
       string(STRIP ${GIT_HASH} GIT_HASH)
       if (NOT GIT_MODIFIED STREQUAL "0")
           set(GIT_HASH "${GIT_HASH}*")
       endif()
    else()
       set(GIT_HASH "unknown")
    endif()
endif()
message(STATUS "Hash = ${GIT_HASH}")

# check Debug vs Release
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
   message(STATUS "DEBUG build enabled")
else()
   message(STATUS "RELEASE build enabled")
endif()

# register protoargs
find_package (Python2 COMPONENTS Interpreter)
if (Python2_FOUND)
   set(PROJECT_PROTOARGS_COMMAND       ${Python2_EXECUTABLE} ${PROJECT_SOURCE_DIR}/Protoargs/bin/protoargs.py)
else() # test if python v3
   find_package (Python3 COMPONENTS Interpreter)
   if (Python3_FOUND)
      set(PROJECT_PROTOARGS_COMMAND       ${Python3_EXECUTABLE} ${PROJECT_SOURCE_DIR}/Protoargs/bin/protoargs3.py)
   else() # assume 2nd version
      set(PROJECT_PROTOARGS_COMMAND       python ${PROJECT_SOURCE_DIR}/Protoargs/bin/protoargs.py) 
   endif()
endif()

# register protobuf
if (WITH_CONAN)
    set(PROJECT_PROTOBUF_COMMAND     ${CONAN_BIN_DIRS_PROTOBUF}/protoc)
else()
    set(PROJECT_PROTOBUF_COMMAND     protoc)
endif()

# ctags
option(WITH_TAGS "Switch tags file generation" OFF)
if (WITH_TAGS)
    message(STATUS "TAGS enabled")
    find_program( TAGS_PATH ctags )
    if(NOT TAGS_PATH)
        message(FATAL_ERROR "ctags not found! Aborting...")
    endif() # NOT TAGS_PATH
    set(PROJECT_TAG_FILENAME    "tags")
    set(PROJECT_TAG_FILE        ${PROJECT_SOURCE_DIR}/${PROJECT_TAG_FILENAME})
    set(PROJECT_TAG_COMMAND     ${TAGS_PATH} -R --languages=c++ --c++-kinds=+p --fields=+iaS --extra=+q . ${PROJECT_INCLUDE_DIR} ${CONAN_INCLUDE_DIRS_BOOST}/boost/filesystem ${CONAN_INCLUDE_DIRS_PROTOBUF})
else()
    message(STATUS "TAGS disabled")
endif()

# code coverage
option(WITH_CODECOV "Switch code coverage generation" OFF)
if (WITH_CODECOV)
    message(STATUS "CODE COVERAGE statistics enabled")
    if (CMAKE_BUILD_TYPE STREQUAL "Debug")
        # Some distributions like Debian ship llvm-cov with the compiler
        # version appended as llvm-cov-x.y. To find this binary we'll build
        # the suggested binary name with the compiler version.
        find_program( LLVMCOV_PATH llvm-cov)
        if(NOT LLVMCOV_PATH )
            string(REGEX MATCH "^[0-9]+.[0-9]+" LLVM_VERSION "${CMAKE_CXX_COMPILER_VERSION}")
            find_program( LLVMCOV_PATH llvm-cov-${LLVM_VERSION})
        endif() # NOT LLVMCOV_PATH
        if(NOT LLVMCOV_PATH )
            message(FATAL_ERROR "llvm-cov not found! Aborting...")
        endif() # NOT LLVMCOV_PATH
        find_program( LCOV_PATH lcov )
        if(NOT LCOV_PATH)
            message(FATAL_ERROR "lcov not found! Aborting...")
        endif() # NOT LCOV_PATH
        find_program( GENHTML_PATH genhtml )
        if(NOT GENHTML_PATH)
            message(FATAL_ERROR "genhtml not found! Aborting...")
        endif() # NOT GENHTML_PATH
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    elseif()
        message(WARNING "Cannot enable code coverage, works only in Debug mode")
    endif()
else()
    message(STATUS "CODE COVERAGE statistics disabled")
endif()

# Address Sanitizer
option(WITH_ASAN "Switch Address Sanitizer build" OFF)
option(WITH_TSAN "Switch Thread Sanitizer build" OFF)
option(WITH_USAN "Switch Undefined Behaviour Sanitizer build" OFF)
if (WITH_ASAN)
   message(STATUS "Address Sanitizer enabled")
   set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -fsanitize=address -fno-omit-frame-pointer")
elseif (WITH_TSAN)
   message(STATUS "Thread Sanitizer enabled")
   set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -fsanitize=thread")
elseif (WITH_USAN)
   message(STATUS "Undefined Behaviour Sanitizer enabled")
   set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -fsanitize=undefined")
else()
   message(STATUS "SANITIZERS disabled")
endif()

# configure a header file to pass some of the CMake settings
# to the source code
configure_file (
    "${PROJECT_SOURCE_DIR}/ProtoargsConfig.h.in"
    "${PROJECT_INCLUDE_DIR}/ProtoargsConfig.h"
)

add_subdirectory(Schema)
add_subdirectory(Tests)
