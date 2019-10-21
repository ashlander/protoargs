Description
===========

**Protoargs** is python proto file compiler, which generates args parser and configuration object filled using protobuf and cxxopts.

The program usualy starts from argument parsing, configuration file creation and configuration class, to store it in memory. It is not hard but time consuming work.

This project should make it easier and less time consuming work with arguments. So the brand new project could be started faster.

It is based on protobuf project and cxxopts project. So the idea - you create *scheme.proto* file, and then using protobuf, you get generated source files with configuration container, using protoargs on the same schema file you will get ".pa.h" and ".pa.cc" files, which contain parsing and protobuf object filling.

If you need storing configuration file with args, you may use **protoconf** to make your life easier.

**Note**: Use proto file version 2 only

PROS:

   + Creates c++ configuration class with all setters and getters for all fields based on schema.
   + Creates c++ args parsing using cxxopts
   + Protoconf compatibility
   + This is protobuf, man, you gain ready to send configuration directly via network, or update it same way from remote host (no, network implememntation you should find on your own).
   + Simplifies creation even complex commands like 'command subcommand [subcommand_args]' (see tests)

CONS:

   - Linux only tested
   - proto file version 2 only supported
   - Dependencies, not standalone (protoc + cxxopts)

Building Tests with Conan (Recomended)
======================================

Build dependencies:

   * conan
   * ctags (optional)

.. code:: bash

     mkdir debug
     cd debug && conan install -s build_type=Debug ../.
     conan build ../.

..

Building Tests extras
=====================

**-o tags=True**        Tags file generation on

**-o codecov=True**     Enable code coverage

**-o clangcheck=True**  Enable clang static analizer build

**-o asancheck=True**   Enable build with Address Santizer

**-o tsancheck=True**   Enable build with Thread Santizer

**-o usancheck=True**   Enable build with Undefined Santizer

Building Tests without Conan
============================

Install dependencies:

   * protobuf with protoc
   * gtest
   * ctags (optional)

See conanfile.py for more information on versions

Building Tests Debug
====================

Go inside **src** directory.

.. code:: bash

    cmake -DWITH_CONAN=OFF -DCMAKE_BUILD_TYPE=Debug CMakeLists.txt

    make
..

Building Release
================

Go inside **src** directory.

.. code:: bash

    cmake -DWITH_CONAN=OFF -DCMAKE_BUILD_TYPE=Release CMakeLists.txt

    make

..

Building extras
===============

**-DWITH_CONAN=ON**     [default = **ON**]     if need build and package with conan

**-DWITH_TAGS=ON**      [default = **OFF**]    if need tags file generation

**-DWITH_CODECOV=ON**   [default = **OFF**]    Enable code coverage

**-DWITH_ASAN=ON**      [default = **OFF**]    Enable build with Address Santizer

**-DWITH_TSAN=ON**      [default = **OFF**]    Enable build with Thread Santizer

**-DWITH_USAN=ON**      [default = **OFF**]    Enable build with Undefined Santizer

Usage
=====

.. code:: bash

   python protoargs.py -o <out DIR> PROTOFILE
               out DIR         [mandatory] path to output directory
               PROTOFILE       [mandatory] path to proto file

..

Also you need c++ files generated from the same proto file using **protoc** compiler. See 

.. code:: bash

   protoc -I=$SRC_DIR --cpp_out=$DST_DIR $SRC_DIR/PROTOFILE

..

You should get 4 files as result: **.pa.cc**, **.pa.h**, **pb.cc**, **pb.h**. Attach them to your project and use.

Example
=======

Suppose we have such a proto file

.. code:: proto

    syntax = "proto2";
    
    package bsw.protoargs.schema;
    
    message dummy // this message is present but will be ignored
    {
        optional string param1 = 1 [default = "default"]; // String param option with default value
        optional uint32 param2 = 2 [default = 10];        // Integer param with default value
        optional int32 param3 = 3;                        // Integer param without default value
        optional float param4 = 4;                        // Float param without default value
    }
    
    // Main message, describing configuration class which will be filled with parsed arguments
    // optional - argument may be missing within command line args
    // required - argument should be present
    // repeated - it may occure several times, but it should be present at least once, so it acts as required, but all the values will be stored
    // types are limited to common type list:
    //    - int32
    //    - uint32
    //    - int64
    //    - uint64
    //    - bool
    //    - string
    // Enums are not supported
    // Name will be filled with parser and accessible from configuration object
    // Default values may be specified
    // Comments on the same line are treated as default value description
    // SO if you want write in comment something nasty, write it above the line
    // The other message companion needed is protoargs_links, however it is optional
    // If protoargs_links missing - all field names from protoargs message will be transformed to lower case, "_" -> "-" , and used as arguments for command line
    // In this situation you will be able to use positional arguments
    // If protoargs_links is present, names for command line arguments will be taken out of them
    // Also all arguments which have no links inside protoargs_links are treated as positional
    // And their names are taken for help transforming them to uppercase (see PARAMG and PARAMH)
    // There may not be more than one positional repeating parameter
    // And position here does matter, currently we expect: PARAMG PARAMH [PARAMH..]
    message protoargs
    {
        optional string paramA = 1 [default = "// tricky default value"];      // String param option with default value. Note: this comment will be taken as description
        optional uint32 paramB = 2 [default = 10];        // Integer param with default value
        optional int32 paramC = 3;                        // Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway
        optional float paramD = 4;                        // Float param without default value
        required string paramE = 5;                       // String param which should be anyway
        repeated int32 paramF = 6;                        // Integer param which may encounter multiple times
        required uint64 PARAMG = 7;                       // Positional integer param, positional param is always \"required\"
        required bool P_A_R_A_M_G_2 = 8;                  // Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false
        optional bool param_I = 9 [default = true];       // Boolean arg with default value (despite it is declared after positional args, that is not a problem)
        optional bool param_J = 10;                       // Boolean arg without default value
        repeated string PARAMH = 11;                      // Positional repeating string params, there may be only one repeating positional param
        optional bool printHelp = 12;                     // Print help and exit
    }//protoargs
    
    // Additional message, optional
    // If missing all names from protoargs message will be converted into long args or if single char to short args
    // Bad things if links are missing:
    //    - no short args
    //    - not possible to set positional args, because positional args are those that present inside protoargs message without links
    // It describes which short and long parameters should be lined to protoargs configuration
    // No metter if this is optional or required or repeated, they will be ignored
    // Sure you will get useless protobuf class for this one, well redundancy happen
    // Name is used as parameter for command line
    // Names will be transformed into lowercase
    // "_" in the name will be changed to "-" for real args
    // all fields are srings, a must
    // Default value is a link to configuration parameter, so it should be exactly the same
    message protoargs_links
    {
        optional string a_long_param = 1 [default = "paramA"];
        optional string a = 2 [default = "paramA"];
        optional string b_long_param = 3 [default = "paramB"];
        optional string c = 4 [default = "paramC"];
        optional string c_long_param = 5 [default = "paramC"];
        optional string d_long_param = 6 [default = "paramD"];
        optional string e = 7 [default = "paramE"];
        optional string f = 8 [default = "paramF"];
        optional string i = 9 [default = "param_I"];
        optional string j_long = 10 [default = "param_J"];
        optional string h = 11 [default = "printHelp"];
        optional string help = 12 [default = "printHelp"];
    }//protoargs

..

Generated c++ code header

.. code:: c++

   #pragma once
   
   #include <string>
   #include <set>
   #include <regex>
   #include <cxxopts.hpp>
   #include "schema.pb.h"
   
   namespace bsw {
   namespace protoargs {
   namespace schema {
   
       class ProtoArgs
       {
           public:
               ProtoArgs() {}
               virtual ~ProtoArgs() {}
   
               /**
                * @brief Get program usage
                * @param program Program name for usage description
                * @return Usage string
                */
               virtual std::string usage(const std::string& program) const;
   
               /**
                * @brief Parse arguments and get object with configuration
                * @param program Program name for usage description
                * @param argc    Command line args num
                * @param argv[]  Command line args
                * @param allowIncomplete  Fills valid configuration fields with no errors, ignoring requires
                * @return Configuration or nullptr if failed
                */
               virtual protoargs* parse(const std::string& program, int argc, char* argv[], bool allowIncomplete = false) const;
   
               /**
                * @brief In case you want add something, or change
                * e.g. set your own usage output
                * look into cxxopts documentation
                * Note: you should parse it manually from now on
                * @param program Program name for usage description
                * @return Options
                */
               virtual cxxopts::Options prepareOptions(const std::string& program) const;
   
               /**
                * @brief Filter result, Note: argv will be destroyed on object destruction
                */
               struct ExcludeResult
               {
                   ~ExcludeResult() { delete [] argv; }
                   int argc;
                   char** argv;
               };//struct
   
               /**
                * @brief Helper function, filter arguments by positions sequence
                * This is useful if you need support multy-commands, like "git add [add args]" and "git commit [commit args]"
                * So at some point you need to remove "add" ot "commit" command argument
                * @param argc Original argc
                * @param argv Original argv
                * @param exclude Array of positions to exclude
                * @return Result with updated argc argv
                */
               virtual ExcludeResult exclude(int argc, char** argv, std::set<int> exclude) const
               {
                   char** argvFiltered = new char*[argc];
                   int pos = 0;
                   int excluded = 0;
                   for (int i = 0; i < argc; ++i)
                      if (exclude.find(i+1) == exclude.end())
                         argvFiltered[pos++] = argv[i];
                      else
                         ++excluded;
   
                   ExcludeResult result;
                   result.argc = argc - excluded;
                   result.argv = argvFiltered;
   
                   return result;
               }
       };//class
   
   }//namespace schema
   }//namespace protoargs
   }//namespace bsw

..


Usage in your code (taken from the tests)

.. code:: c++

       const char* argv[] = {
          "program"
          ,"-e", "valueE"
          ,"--a-long-param", "somevalue"
          ,"--b-long-param", "4"
          ,"-c", "555"
          ,"--d-long-param", "555.5"
          ,"-f", "1"
          ,"-f", "2"
          ,"-f", "3"
          ,"-i"
          ,"--j-long"
          , "50" // paramG
          , "0" // bool paramG
          , "pos1", "pos2", "pos3"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);

       // These 2 lines is all you hopefully need
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );

       // config is protobuf parser, as you can see how we access fields
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE( config->has_parama() );
       ASSERT_EQ( "somevalue", config->parama() );

       ASSERT_TRUE( config->has_paramb() );
       ASSERT_EQ( 4u, config->paramb() );

       ASSERT_TRUE( config->has_paramc() );
       ASSERT_EQ( 555, config->paramc() );

       ASSERT_TRUE( config->has_paramd() );
       ASSERT_EQ( 555.5f, config->paramd() );

       ASSERT_TRUE( config->has_parame() );
       ASSERT_EQ( "valueE", config->parame() );

       ASSERT_EQ( 3, config->paramf_size() );

       ASSERT_TRUE( config->has_param_i() );
       ASSERT_TRUE( config->param_i() );

       ASSERT_TRUE( config->has_param_j() );
       ASSERT_TRUE( config->param_j() );

..

Your application usage output

.. code:: plain

    program [OPTION...] PARAMG P_A_R_A_M_G_2 PARAMH [PARAMH...]
   
    -a, --a-long-param [paramA]  String param option with default value. Note:
                                 this comment will be taken as description
                                 {OPTIONAL,type:string,default:'// tricky default
                                 value'}
   
        --b-long-param [paramB]  Integer param with default value
                                 {OPTIONAL,type:uint32,default:'10'}
   
    -c, --c-long-param [paramC]  Integer param without default value. Avoid new
                                 lines they are rendered not correctly in help.
                                 Words will be transfered to new line anyway
                                 {OPTIONAL,type:int32,default:''}
   
        --d-long-param [paramD]  Float param without default value
                                 {OPTIONAL,type:float,default:''}
   
    -e, [paramE]                 String param which should be anyway
                                 {REQUIRED,type:string}
   
    -f, [paramF]                 Integer param which may encounter multiple
                                 times {REPEATED,type:int32,default:''}
   
    -i,                          Boolean arg with default value (despite it is
                                 declared after positional args, that is not a
                                 problem) {OPTIONAL,type:bool,default:'true'}
   
        --j-long                 Boolean arg without default value
                                 {OPTIONAL,type:bool,default:''}
   
    -h, --help                   Print help and exit
                                 {OPTIONAL,type:bool,default:''}
   
                PARAMG           Positional integer param, positional param is
                                 always "required" {REQUIRED,type:uint64}
   
                P-A-R-A-M-G-2    Positional boolean param, positional param is
                                 always "required", Note: param set - true,
                                 missing - false {REQUIRED,type:bool}
   
                PARAMH           Positional repeating string params, there may
                                 be only one repeating positional param
                                 {REQUIRED,type:string}
   
..

See more tests for even more complex examples.
