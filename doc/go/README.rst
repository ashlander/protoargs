Description
===========

**Protoargs** is python proto file compiler, which generates arguments parser using flag_.

This documentation part shows go parser generation and usage based on existing configuration. Start from main_ page for better description and proto file configuration rules.


.. _flag: https://pkg.go.dev/flag

.. _main: https://github.com/ashlander/protoargs/tree/master

**PROS**:

+ Creates go args parser using flag_.
+ Flag is standard package available
+ Required and optional arguments
+ Repeated arguments
+ Positional arguments
+ Usage includes positional arguments block
+ Simplifies creation even complex commands like 'command subcommand [subcommand_args]'

**CONS**:

- flag_ is actually very basic, unfortunately some limitations are applied

**LIMITATIONS**:

- Nonpositional repeated boolean flags like '--flag --flag --flag' are not supported, use '--flag=true --flag=false --flag=true' instead

Usage
=====

.. image:: ../../src/Protoargs/img/goschema.png
   :align: center

First of all, you are interested in python script files in this project, python scripts are located in bin_ directory.

.. _bin: ../../src/Protoargs/bin/

.. code:: bash

   python protoargs.py -o <out DIR> -i PROTOFILE --go
               out DIR         [mandatory] path to output directory
               PROTOFILE       [mandatory] path to proto file

..

You should get 1 file as result: **_pa.go**. Attach it to your project and now you are ready to move forward.

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
        optional float PARAM_FLOAT = 15;                  // Positional float param
        optional double PARAM_DOUBLE = 16;                // Positional double param
        repeated string PARAMH = 11;                      // Positional repeating string params, there may be only one repeating positional param
        optional bool printHelp = 12;                     // Print help and exit
        optional float paramFloat = 13;                   // Float param
        optional double paramDouble = 14;                 // Double param
    }//protoargs
    
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

Your application usage output will be generated for you

.. code:: plain

    usage: program -e paramE [-a|--a-long-param paramA] [--b-long-param paramB]
                             [-c|--c-long-param paramC] [--d-long-param paramD]
                             [-f paramF [-f paramF ...]] [-i] [--j-long]
                             [-h|--help] [-k paramFloat] [-l paramDouble] PARAMG
                             P_A_R_A_M_G_2 PARAM_FLOAT PARAM_DOUBLE PARAMH
                             [PARAMH ...]

    Desription

    required arguments:
      -e paramE              String param which should be anyway
                             {REQUIRED,type:string})

    required positional arguments:
      PARAMG                 Positional integer param, positional param is always
                             \"required\" {REQUIRED,type:uint64})
      P_A_R_A_M_G_2          Positional boolean param, positional param is always
                             \"required\", Note: param set - true, missing - false
                             {REQUIRED,type:bool})
      PARAM_FLOAT            Positional float param {REQUIRED,type:float})
      PARAM_DOUBLE           Positional double param {REQUIRED,type:double})
      PARAMH                 Positional repeating string params, there may be only
                             one repeating positional param {REQUIRED,type:string})

    optional arguments:
      -a, --a-long-param paramA
                             String param option with default value. Note: this
                             comment will be taken as description
                             {OPTIONAL,type:string,default:"// tricky default
                             value"})
      --b-long-param paramB  Integer param with default value
                             {OPTIONAL,type:uint32,default:10})
      -c, --c-long-param paramC
                             Integer param without default value. Avoid new lines
                             they are rendered not correctly in help. Words will be
                             transfered to new line anyway
                             {OPTIONAL,type:int32,default:0})
      --d-long-param paramD  Float param without default value
                             {OPTIONAL,type:float,default:0})
      -f paramF              Integer param which may encounter multiple times
                             {REPEATED,type:int32})
      -i                     Boolean arg with default value (despite it is declared
                             after positional args, that is not a problem)
                             {OPTIONAL,type:bool,default:true})
      --j-long               Boolean arg without default value
                             {OPTIONAL,type:bool,default:false})
      -h, --help             Print help and exit
                             {OPTIONAL,type:bool,default:false})
      -k paramFloat          Float param {OPTIONAL,type:float,default:0})
      -l paramDouble         Double param {OPTIONAL,type:double,default:0})

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

Now what you need is the file ending with **_pa.go**, it contains interface you need. It will look like several functions which you may use. Note: namespaces are not used currently, but file name is used as package name.

.. code:: go

    func Usage(program string, description string) string

    func Parse(program string, description string, allow_incomplete bool) (*Config, error)

..

They are quite clear, **Usage** outputs help message, and the **Parse** parses arguments. Both accept program name and description which you want to see in help, as long as **Parse** method may call **Usage** internally if something goes wrong.

**allow_incomplete** option if set to true, will return all successfully parsed arguments ignoring failed ones, which is useful to search for **--help** or **--version** arguments, because with required fields missing, parser will produce error. On error, usage will be displayed automatically with the error description.

Let's go for code:

.. code:: go

    import (
        "fmt"
        "./simple_pa"
    )

    func main() {
        { // looking only for help, avoid error checks
            config, _ := simple_pa.Parse(`program`, `description`, true)

            if config.Arghelp.IsSet() {
                fmt.Println( simple_pa.Usage(`program`, `description`) )
                return
            }
        }

        { // do second strict and final parsing
            config, err := simple_pa.Parse(`program`, `description`, false)

            if err != nil {
                fmt.Println(`SimpleUsage: %s`, err)
                return
            }

            fmt.Println(config)
            if config.Argp.IsSet() {
                fmt.Println(`p = `, config.Argp.Get())
            }

            ...
        }
    }

..

Well that should be simple enough to start your going.

**Note:** In order to export configuration values Go requires first letters to be uppercase, but that's a bad idea to transform arguments like this, because then a problem with similar arguments will appear, e.g. '-t' and '-T' options. So in order to solve this 'Arg' prefix was added to each variable of Config struct. Above you can see that variable for '-p' argument will be 'Argp'.

**Note:** For your convenience configuration structure is code generated with all the values retrieved from command line, but each variable (accept for repeated values, which are arrays) is represented as custom entity, and in order to access the actual value you need to call **Get()** function. Additionally you can discover if argument was specified as command line argument with **IsSet()** function, if not set **Get()** will return default value.

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

The idea behind it is a little bit tricky, but it is working well enough.

So first of all you need 3 *.proto* files with own command settings, plain **program**, **program create**, **program copy**.

Here is *main*:

.. code:: proto

   syntax = "proto2";

   package bsw.protoargs.main;

   message protoargs
   {
       optional bool help = 1 [default = false];         // Print help and exit
       required string COMMAND = 2;                      // Command (create, copy)
   }//protoargs

   message protoargs_links
   {
       optional string h = 11 [default = "help"];
       optional string help = 12 [default = "help"];
   }//protoargs

..

So here we do expect no or single argument for main program, it may be -h/--help or command. This limitation gives us advantage.

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

After generating all 3 go parser files, let's think about these command parsing:

.. code:: bash

   program --help
   program create --help

..

For the first iteration we need to parse with main program parser. But it is created to parse the first and not the second. It will fail on **program create --help**. So as far as we have limited us to 2 options we may parse first 2 options only. But here we need some manipulation to do with arguments list. There is parse function extension exists called **ParseExt**, it accepts args slice as parameter.

**Note:** flag_ needs you as user to remove first arg[0] from the arguments list before parsing, you should not do this here. The reason is to be similar with other languages parsers usage.

.. code:: go

    import (
        "fmt"
        "./multy_command_pa"
        "./multy_command_create_pa"
        "./multy_command_copy_pa"
    )

    func main() {
        program := "program"
        description := "main command to manipulate files"
        argv := os.Args
        command := ""

        { // looking only for help, avoid error checks
            // limit arguments list to 2 arguments
            config, _ := multy_command_pa.ParseExt(program, argv[:2], description, true)

            if config.Arghelp.IsSet() {
                fmt.Println( multy_command_pa.Usage(program, description) )
                return
            }

            // potentially we could check for command here, with additional IsSet check
            // as we expect only help or command argument and do additional error checking
            // but not this time, the more complex is the parser the less you would like
            // to do such a things
        }

        { // do second strict and final parsing
            config, err := multy_command_pa.Parse(program, argv[:2], description, false)

            if err != nil {
                fmt.Println(`MultyUsage: %s`, err)
                return
            }

            // after strict parsing, no need to check if required argument is present
            // we know it is, other way error would be
            command = config.ArgCOMMAND.Get() 
        }

        ...
    }

..

Ok, we have discovered command, now that's time for subcommand parsing. The only problem here is that we have positional argument (which is command) standing not at the end, so we can't create proper schema to parse. But as long as we found proper command we do not need it any more, so how about removing it from arguments?

.. code:: python

    import (
        "fmt"
        "./multy_command_pa"
        "./multy_command_create_pa"
        "./multy_command_copy_pa"
    )

    func main() {

        ...

        program += " " + command
        argv_nocmd := append(argv[:1], argv[2:]...) // remove command name from arguments

        if command == "create" {
            description = "create files command"
            { // looking only for help, avoid error checks
                config, _ := multy_command_create_pa.ParseExt(program, argv_nocmd, description, true)

                if config.Arghelp.IsSet() {
                    fmt.Println( multy_command_create_pa.Usage(program, description) )
                    return
                }
            }

            { // do second strict and final parsing
                config, err := multy_command_pa.Parse(program, argv_nocmd, description, false)

                if err != nil {
                    fmt.Println(`Create MultyUsage: %s`, err)
                    return
                }

                ... // we can use config structure

            }
        } else if command == "copy" {

            ... // the same as above but with multy_command_copy_pa parser

        } else {
            // TODO error: no such command
            return
        }
    }

..

Extreme Usage
=============

Sometimes people need some real complex argument parsing, like

.. code:: bash

   program [program options] command [command options]

..

Well, I have not tested it this way, but you may achieve it. The trick is you need to calculate number of *[program options]* manually. This way you can exclude needed number of arguments, and proceed as previous example.

