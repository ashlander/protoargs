cmake_minimum_required(VERSION 2.6)
project (Schema)

# local includes
set (PROJECT_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/include)
set (PROJECT_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

set(SCHEMA_SRCS
    ${PROJECT_SOURCE_DIR}/schema.pb.cc
    ${PROJECT_SOURCE_DIR}/simple.pb.cc
    ${PROJECT_SOURCE_DIR}/multy_command.pb.cc
    ${PROJECT_SOURCE_DIR}/multy_command_create.pb.cc
    ${PROJECT_SOURCE_DIR}/multy_command_copy.pb.cc
)

set(PARSER_SRCS
    ${PROJECT_SOURCE_DIR}/schema.pa.cc
    ${PROJECT_SOURCE_DIR}/simple.pa.cc
    ${PROJECT_SOURCE_DIR}/multy_command.pa.cc
    ${PROJECT_SOURCE_DIR}/multy_command_create.pa.cc
    ${PROJECT_SOURCE_DIR}/multy_command_copy.pa.cc
)

set(SCHEMA_PROTO
    ${PROJECT_SOURCE_DIR}/schema.proto
    ${PROJECT_SOURCE_DIR}/simple.proto
    ${PROJECT_SOURCE_DIR}/multy_command.proto
    ${PROJECT_SOURCE_DIR}/multy_command_create.proto
    ${PROJECT_SOURCE_DIR}/multy_command_copy.proto
)

include_directories("${PROJECT_BINARY_DIR}")
include_directories("${PROJECT_INCLUDE_DIR}")

include_directories(${CONAN_INCLUDE_DIRS_PROTOBUF})
include_directories(${CONAN_INCLUDE_DIRS_CXXOPTS_RELEASE})

# protobuf
set_source_files_properties( ${SCHEMA_SRCS} PROPERTIES GENERATED true)
add_custom_command (    OUTPUT              ${SCHEMA_SRCS}
                        COMMAND             ${PROJECT_PROTOBUF_COMMAND}
                        ARGS                -I${PROJECT_SOURCE_DIR} --cpp_out=${PROJECT_SOURCE_DIR} ${SCHEMA_PROTO}
                        DEPENDS             ${SCHEMA_PROTO}
                        WORKING_DIRECTORY   ${CMAKE_SOURCE_DIR} )

# protoargs
set_source_files_properties( ${PARSER_SRCS} PROPERTIES GENERATED true)
foreach(PROTOPATH ${SCHEMA_PROTO})
   message(STATUS "Generating fom ${PROTOPATH}")
   string(STRIP ${PROTOPATH} PROTOPATH)
   string(REGEX REPLACE "\\.[^.]*$" "" SCHEMA ${PROTOPATH}) # remove file extension
   add_custom_command (    OUTPUT              ${SCHEMA}.pa.cc
                           COMMAND             ${PROJECT_PROTOARGS_COMMAND}
                           ARGS                -o ${PROJECT_SOURCE_DIR} -i ${PROTOPATH}
                           DEPENDS             ${SCHEMA_PROTO}
                           WORKING_DIRECTORY   ${CMAKE_SOURCE_DIR} )
endforeach()

# tags generation
if (WITH_TAGS)
    set_source_files_properties( ${PROJECT_TAG_FILE} PROPERTIES GENERATED true)
    add_custom_command ( OUTPUT ${PROJECT_TAG_FILE}
        COMMAND ${PROJECT_TAG_COMMAND}
        DEPENDS ${NETWORK_SRCS}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} )
endif()

add_library(${PROJECT_NAME} STATIC ${PROJECT_TAG_FILE} ${SCHEMA_SRCS} ${PARSER_SRCS})
target_link_libraries(${PROJECT_NAME} ${EXTRA_LIBS})




