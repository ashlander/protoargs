Description
===========

**Protoargs** is python proto file compiler, which generates arguments parser using clap_.

This documentation part shows rust parser generation and usage based on existing configuration. Start from main_ page for better description and proto file configuration rules.


.. _clap: https://docs.rs/clap/latest/clap/

.. _main: https://github.com/ashlander/protoargs/tree/master

**PROS**:

+ Creates rust args parser using clap_.
+ As parsing result return ready-to-use configuration instance with correct type fields
+ Simplifies creation even complex commands like 'command subcommand [subcommand_args]'

**CONS**:

- clap_ is actually way more powerful
- Dependencies, not standalone (clap_)

Usage
=====

.. image:: ../../src/Protoargs/img/rustschema.png
   :align: center

First of all, you are interested in python script file in this project, python scripts are located in bin_ directory.

.. _bin: ../../src/Protoargs/bin/

.. code:: bash

   python protoargs.py -o <out DIR> -i PROTOFILE --rust
               out DIR         [mandatory] path to output directory
               PROTOFILE       [mandatory] path to proto file

..

You should get 1 file as result: **_pa.rs**. Attach it to your project and now you are ready to move forward. 

Example of Usage Output
=======================

Suppose we have such a proto file (do not be afraid, this is just to show you possible output).

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
        optional float PARAM_FLOAT = 15;                   // Positional float param
        optional double PARAM_DOUBLE = 16;                 // Positional double param
        repeated string PARAMH = 11;                      // Positional repeating string params, there may be only one repeating positional param
        optional bool printHelp = 12;                     // Print help and exit
        optional float paramFloat = 13;                   // Float param
        optional double paramDouble = 14;                 // Double param
    }//protoargs
    
    // Additional message, optional
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
        optional string k = 13 [default = "paramFloat"];
        optional string l = 14 [default = "paramDouble"];
    }//protoargs

..

Your application usage output

.. code:: plain

    program 
    Desription
    
    USAGE:
        program [OPTIONS] -e <paramE> <PARAMG> <P-A-R-A-M-G-2> <PARAM-FLOAT> <PARAM-DOUBLE> <PARAMH>...
    
    ARGS:
        <PARAMG>           Positional integer param, positional param is always \"required\"
                           {REQUIRED,type:uint64}
        <P-A-R-A-M-G-2>    Positional boolean param, positional param is always \"required\", Note:
                           param set - true, missing - false {REQUIRED,type:bool}
        <PARAM-FLOAT>      Positional float param {REQUIRED,type:float}
        <PARAM-DOUBLE>     Positional double param {REQUIRED,type:double}
        <PARAMH>...        Positional repeating string params, there may be only one repeating
                           positional param {REQUIRED,type:string}
    
    OPTIONS:
        -a, --a-long-param <paramA>    String param option with default value. Note: this comment will
                                       be taken as description {OPTIONAL,type:string,default:"// tricky
                                       default value"}
            --b-long-param <paramB>    Integer param with default value
                                       {OPTIONAL,type:uint32,default:"10"}
        -c, --c-long-param <paramC>    Integer param without default value. Avoid new lines they are
                                       rendered not correctly in help. Words will be transfered to new
                                       line anyway {OPTIONAL,type:int32,default:""}
            --d-long-param <paramD>    Float param without default value
                                       {OPTIONAL,type:float,default:""}
        -e <paramE>                    String param which should be anyway
                                       {REQUIRED,type:string,default:""}
        -f <paramF>                    Integer param which may encounter multiple times
                                       {REPEATED,type:int32,default:""}
        -i                             Boolean arg with default value (despite it is declared after
                                       positional args, that is not a problem)
                                       {OPTIONAL,type:bool,default:"true"}
            --j-long                   Boolean arg without default value {OPTIONAL,type:bool,default:""}
        -k <paramFloat>                Float param {OPTIONAL,type:float,default:""}
        -l <paramDouble>               Double param {OPTIONAL,type:double,default:""}
        -h, --help                     Print help information

..

Simple Example
==============

Let's take our first simple example (as a reminder *-p NUM* and *--param=NUM* arguments are different and will be stored in different values):

.. code:: proto

    syntax = "proto2";

    package bsw.protoargs.schema;

    // Main message, describing configuration class which will be filled with parsed arguments
    message protoargs
    {
        optional bool help = 1;                         // Show help message and exit,        it is transformed into --help long argument
        optional bool version = 2;                      // Show version message and exit,     it is transformed into --version long argument
        optional bool who_am_i = 3;                     // Show custom user message and exit, it is transformed into --who-am-i long argument
        optional uint p = 4 [default = 10];             // Integer param with default value,  it is transformed into -p short argument, even if not specified it will return with value 10
        optional uint32 param = 5 [default = 10];       // Integer param with default value,  it is transformed into --param short argument, even if not specified it will return with value 10
        optional string UPCASE = 6 [default = "Test"];  // Integer param with default value,  it is transformed into --upcase long argument, even if not specified it will return with value "Test"
    }//protoargs

..

Now what you need is the file ending with **_pa.rs**, it contains interface you need. It will look like several functions which you may use. Note: namespaces are not used currently.

**Note:** *-h/--help* arguments are predefined within the clap_, so variant from proto file will be skipped, and warning message output

.. code:: rust

   pub fn usage(program: &str, description: &str) -> String

   pub fn parse(program: &str, description: &str) -> Result<Config, String>

..

They are quite clear, **usage** outputs help message, and the **parse** parses arguments and outputs filled strong typed structure instance. Both accept **program name** and **description** which you want to see in help, as long as **parse** method may call **usage** internally if something goes wrong.

There are some other parse functions containing **allow_incomplete** option, if set to true, will return all successfully parsed arguments ignoring failed ones, like missing required arguments, but if will still return error if type mismatch happens.

Let's go for code:

.. code:: rust

    mod simple_pa;
    use crate::simple_pa::simple_pa::parse;
    
    fn main() {
        // parsing arguments
        let program_name = "graphql_server";
        let program_description = "GraphQL server Rust implementation";

        // Note: no error handling
        let config = parse(program_name, program_description).ok().unwrap();

        println!("{}", config.p().to_string());
    }

..

Well that should be simple enough to start your going.

Complex Example
===============

Here comes something big. Current implementations allows us to make complex parsing easily. Like

.. code:: bash

   program --help
   program create --help
   program create [create arguments]
   program copy --help
   program copy [copy arguments]

..

The biggest advantage of clap_ is subcommands integrated, but you still may use protoargs to your advantage.

The idea behind it is a little bit tricky, but it is working well enough.

So first of all you need **3** *.proto* files with own command settings, plain **program**, **program create**, **program copy**.

Here is *main*:

.. code:: proto

   syntax = "proto2";

   package bsw.protoargs.main;

   message protoargs
   {
       optional bool help = 1 [default = false];         // Print help and exit
   }//protoargs

   message protoargs_links
   {
       optional string h = 11 [default = "help"];
       optional string help = 12 [default = "help"];
   }//protoargs

..

Let's go for the rest proto files.

For program create:

.. code:: proto

   syntax = "proto2";

   package bsw.protoargs.main.create;

   message protoargs
   {
       optional bool help = 1 [default = false];         // Print help and exit
       optional uint64 size = 2 [default = 0];           // Size of the file
       required string PATH = 3;                         // Path to file to create
   }//protoargs

   message protoargs_links
   {
       optional string h = 1 [default = "help"];
       optional string help = 2 [default = "help"];
       optional string s = 3 [default = "size"];
       optional string size = 4 [default = "size"];
   }//protoargs

..

For program copy:

.. code:: proto

   syntax = "proto2";

   package bsw.protoargs.main.copy;

   message protoargs
   {
       optional bool help = 1 [default = false];         // Print help and exit
       optional bool recursive = 2 [default = false];    // Recursive copy
       required string SRC = 3;                          // Path to source path
       required string DST = 4;                          // Path to destination path
   }//protoargs

   message protoargs_links
   {
       optional string h = 1 [default = "help"];
       optional string help = 2 [default = "help"];
       optional string r = 3 [default = "recursive"];
       optional string recursive = 4 [default = "recursive"];
   }//protoargs

..

After generating all 3 files, let's unite all them to one parsing mechanics. To get final configuration instance we need do some staged manual parsing. For this particular needs *parse_matches* function exists, the only special thing is you need to provide arguments as str slice (this code takes predefined args):

.. code:: rust

    let description = "Desription";
    let argv = vec![ "program"
       , "copy"
       ,"-r"
       , "/tmp/tmp.file.src"
       , "/tmp/tmp.file.dst"
    ];

    // prepare command with subcommands
    let create_command = crate::multy_command_create_pa::multy_command_create_pa::prepare_options("create", description);
    let copy_command = crate::multy_command_copy_pa::multy_command_copy_pa::prepare_options("copy", description);
    let command = crate::multy_command_pa::multy_command_pa::prepare_options(argv[0], description)
        .subcommand(create_command)
        .subcommand(copy_command);
    
    // do parsing
    let matches = command.get_matches_from(&argv[..]);
    
    { // process values and generate general command config (without subcommands)
        let rconfig = crate::multy_command_pa::multy_command_pa::parse_matches(&matches, false);
        let config = rconfig.ok().unwrap();
        ...
    }
    
    {// process subcommands
        if let Some(matches) = matches.subcommand_matches("copy") {
            // process values and generate copy subcommand config
            let rconfig = crate::multy_command_copy_pa::multy_command_copy_pa::parse_matches(&matches, false);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();
            ...
        } else if let Some(matches) = matches.subcommand_matches("create") {
            // process values and generate copy subcommand config
            let rconfig = crate::multy_command_create_pa::multy_command_create_pa::parse_matches(&matches, false);
            let config = rconfig.ok().unwrap();
            ...
        }
    }

..

Extreme Usage
=============

Sometimes people need some real complex argument parsing, like

.. code:: bash

   program [program options] command [command options]

..

In case of rust that's working just the same way as above, just add couple new params to main *program.proto*, and repeat. You are done.

Building Tests
==============

Proceed to Tests_.

Just run:

.. code:: bash

   cargo build
   cargo test

..

.. _Tests: ../../src/TestsRust/

