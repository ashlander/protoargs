Intro
=====

C++ program usually starts from argument parsing, configuration file creation and configuration class, to store it in memory. It is not hard but time consuming work.

This project should make it easier and less time consuming to work with arguments. So the brand new project could be started faster, it allows easy parameters extension, so complex command branches may be as easy as change configuration. It should be simple to code as well.

If you need flexible and easy way NOT to write argument parser and automate help output, do want to rely on configuration rather than code - welcome, you are in the right spot.

.. image:: src/Protoargs/img/intro.png
   :align: center

Description
===========

**Protoargs** is python proto file compiler, which generates arguments parser and configuration ready in-code structures using protobuf_ and cxxopts_.

The idea - you create *any_name_scheme.proto* file and then, using **protoc**, you get generated source files with configuration container ".pb.h" and ".pb.cc", using **protoargs** on the same schema file, you will get additional ".pa.h" and ".pa.cc" files, which contain argument parsing.

.. _protobuf: https://github.com/protocolbuffers/protobuf

.. _cxxopts: https://github.com/jarro2783/cxxopts

.. image:: src/Protoargs/img/general.png
   :align: center

If you need storing configuration file with args, you may use Protoconf_ to make your life easier.

**PROS**:

+ Creates c++ configuration class with all setters and getters for all fields based on schema.
+ Creates c++ args parsing using cxxopts
+ This is protobuf, you get ready to send configuration directly via network, or update it same way from remote host (no, network implementation you should find on your own).
+ Simplifies creation even complex commands like 'command subcommand [subcommand_args]'
+ Protoconf_ compatibility

.. _Protoconf: https://github.com/ashlander/protoconf

**CONS**:

- Tested and used on Linux only (be my guest to try it out on other OS, and I will gladly remove this line)
- Proto file version 2 only supported
- Dependencies, not standalone (protobuf + cxxopts)

Configuration File Rules
========================

The configuration is based on protobuf proto file.

If you do not know what is **protobuf** project and **proto** configuration file, I would recommend reading about it at protobuf_. However this is not show stopper, you may proceed without knowing it well. But if you are stuck with configuration please read about proto_ file creation.

.. _proto: https://developers.google.com/protocol-buffers/docs/proto

1. **Use proto file version 2 only**.

2. **package** directive is parsed and correct namespaces are used.

3. Message **protoargs** and **protoargs_links** are predefined and should not be used for other purposes other than arguments parsing.

4. Other messages in the same proto file will be ignored.

5. Meaning of existing proto file directives using protoargs:

   + **optional** - argument may be missing within command line args, and is optional, you may specify default value for the parameter if missing. By default it will contain 0 for integers or empty string.
   + **required** - argument should be present, and is mandatory.
   + **repeated** - it may occur several times, but it should be present at least once, so it acts as **required**, but all the values will be stored in array for you.

6. Types are limited to common type list:

   + **int32**
   + **uint32**
   + **int64**
   + **uint64**
   + **bool**
   + **string**

7. **Enums** are not supported.

8. Values specified in **upper case** will be transformed into **lower case** parameters

9. Values containing **"_"** will be transformed to contain **"-"** instead

10. Custom default values may be specified for optional arguments. They will be shown during help message, as well as expected argument type.

11. Comments at the same line are treated as default value description ( SO if you want write in comment something nasty, write it above the line ).

12. Comments which are used for help description may not be multi-line.

message protoargs
=================

This is the main message, describing configuration class which will be filled with parsed arguments. **protoargs.py** script will search for this message name, and will fail if missing.

Let's start from simple one.

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

This will automatically allows us parse specified arguments:

.. code:: bash

   ./program --help
   ./program --version
   ./program --who-am-i
   ./program -p 12 --param=11
   ./program -p 12 --param=11 --who_am_i

..

This is very nice for the start, but here is the problem: what if we want **-p** and **--param** arguments point to the same structure variable, because now they have separate and may carry different values, so currently we need to check both to decide the final value.

The other problem: what if we need some positional values, like:

.. code:: bash

   ./program SRC DST

..

For these purposes another message is prepared, called **protoargs_links**.

message protoargs_links
=======================

This is optional message, which is needed for advanced arguments parsing.

It describes which short and long parameters should be linked to protoargs configuration.
For all message fields no matter if this is optional or required or repeated, the types are being **ignored**.
Field names from **protoargs_links** are now used as argument names for command line, and **protoargs** names will be used for in-code structure getters.
All fields are **strings**, a must.
Default value is a link to configuration parameter inside **protoargs**, and it should be **exactly the same**.

Now let's update our configuration, so that **-p** and  **--param** arguments will be bind to the same structure variable.

.. code:: proto

    syntax = "proto2";

    package bsw.protoargs.schema;

    // Main message, describing configuration class which will be filled with parsed arguments
    message protoargs
    {
        optional bool printHelp = 1;                       // Show help message and exit,        it is transformed into --help long argument
        optional bool printVersion = 2;                    // Show version message and exit,     it is transformed into --version long argument
        optional bool who_am_iVal = 3;                     // Show custom user message and exit, it is transformed into --who-am-i long argument
        optional uint32 paramVal = 4 [default = 10];       // Integer param with default value,  it is transformed into --param short argument, even if not specified it will return with value 10
        optional string UPCASEVAL = 5 [default = "Test"];  // Integer param with default value,  it is transformed into --upcase long argument, even if not specified it will return with value "Test"
    }//protoargs

    // Additional message, optional
    message protoargs_links
    {
        optional string help = 1 [default = "printHelp"];       // This comment will be ignored
        optional string version = 2 [default = "printVersion"]; // This comment will be ignored
        optional string who_am_i = 3 [default = "who_am_iVal"]; // This comment will be ignored
        optional string p = 4 [default = "paramVal"];           // This comment will be ignored
        optional string param = 5 [default = "paramVal"];       // This comment will be ignored
        optional string UPCASE = 6 [default = "UPCASEVAL"];     // This comment will be ignored
    }//protoargs

..

That's it. Now *paramVal* will be transformed into *paramval()* in-code method, but it will be filled when *-p NUM* or *--param=NUM* option specified. Field names inside **protoargs** message were changed to show you that now you can name them more verbose, and it will not influence actual command line argument names. So the command usage string will have exact the same names:

.. code:: bash

   ./program --help
   ./program --version
   ./program --who-am-i
   ./program -p 12 --param=11 # Note: this is not valid now, they can not be used both at the same time, use repeated instead of optional to achieve this
   ./program -p 12
   ./program --param=11

..


Positional arguments
====================

Suppose you need this kind of arguments to parse:

.. code:: bash

   ./program DST SRC [SRC..]

..

Where DST and SRC are not short/long parameters but defined rather by position. To make it more complex, let the user to specify SRC multiple times.

First thing to know about is - **positional** arguments are **always mandatory**, so even if you specify optional type, parser will generate code as if it was required type. Sure if positional argument could be optional, well you could not rely on position anymore.

The other nice feature is having positional argument to be repeated multiple times, which is actually possible. This brings us to limitation, **there should be only one repeating positional argument, and it may be only at the end**.

Positional argument may be defined only using both **protoargs** and **protoargs_links** messages. All fields from **protoargs** message which are not linked inside **protoargs_links** are treated as **positional**. And their position inside **protoargs** message will be preserved as argument parsing, so place repeated positional arguments at the end, if you do want make it working. Be warned that position number of the protobuf field is not parsed, so if you change the lines, you will break things, even if numbers are preserved, you need correct line order for now (for the example below, do not swap SRC and DST lines).

.. code:: proto

    syntax = "proto2";

    package bsw.protoargs.schema;

    // Main message, describing configuration class which will be filled with parsed arguments
    message protoargs
    {
        required string DST = 1;          // Positional argument
        repeated string SRC = 2;          // Positional repeating argument
    }//protoargs


    // Additional message, optional
    message protoargs_links
    {
    }//protoargs

..

**Note**: even if all your arguments are positional, you need empty **protoargs_links** message to be present in order for parser to understand your intentions. Other way you will get command line parser search for *--dst=STRING* and *--src=STRING* arguments.

Usage
=====

First of all, you are interested in one single file in this project, python script located in bin_ directory.

.. _bin: src/Protoargs/bin/

.. code:: bash

   python protoargs.py -o <out DIR> -i PROTOFILE
               out DIR         [mandatory] path to output directory
               PROTOFILE       [mandatory] path to proto file

..

Also you need files generated from the same proto file using **protoc** compiler.

.. code:: bash

   protoc -I=$SRC_DIR --cpp_out=$DST_DIR $SRC_DIR/PROTOFILE

..

You should get 4 files as result: **.pa.cc**, **.pa.h**, **pb.cc**, **pb.h**. Attach them to your project and now you are ready to move forward. Do not forget installed dependencies like **protobuf** and **cxxopts**.

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

Now what you need from 4 generated files is the one with **.pa.h** file, it contains interface you need. It will look like **class ProtoArgs** protected with specified namespaces **bsw.protoargs.schema**. Inside you will find main access methods:

.. code:: c++

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

..

They are quite clear, **usage** outputs help message, and the **parse** parses arguments. Both accept program name which you want to see in help, as long as **parse** method may call **usage** internally if something goes wrong.

**allowIncomplete** option if set to true, will return all successfully parsed arguments ignoring failed ones, other way null will be returned. This option is useful if tested for --help/--version arguments when having required arguments as well. It will return configuration and not null saying required argument missing. The idea is to test twice, at first with **allowIncomplete** and check for --help/--version, and next check without, making it do full check. Still even with **allowIncomplete** it may output errors anyway if wrong arguments specified.

**Note**: configuration returned is created with **new** and should be destroyed afterwards. It is highly recommended to use **unique_ptr** or **shared_ptr** to ease your life.

Let's go for code:

.. code:: c++

    simple::ProtoArgs arguments;
    auto config = std::unique_ptr<simple::protoargs>( arguments.parse(argv[0], argc, (char**)argv) );
    if (!config)
    {
       // you do not need usage output, it is already on the screen
       return EXIT_FAILURE;
    }

    if (argc == 1 || config->has_help()) // if no argument or --help specified print help end exit
    {
       std::cout << arguments.usage(argv[0]);
       return EXIT_SUCCESS;
    }

    if (config->has_version()) // if version specified
    {
       std::cout << "Some version";
       return EXIT_SUCCESS;
    }

    if (config->has_param())
    {
       std::cout << "Param = " << config->param();
    }

    ...
..

Well that should be simple enough to start your going.

Advanced Usage
==============

In case this all is not how you would like it, and e.g. **usage** method output does not satisfy you. You may start doing it all by yourself. Fist of all - you can redefine **usage** method, it is virtual and all you need is override and change it. You may loose flexibility unfortunately if schema will change.

The other method is to get **cxxopts** internals with **prepareOptions** method. From now on read cxxopts_ documentation on how to proceed.

.. code:: c++

    /**
     * @brief In case you want add something, or change
     * e.g. set your own usage output
     * look into cxxopts documentation
     * Note: you should parse it manually from now on
     * @param program Program name for usage description
     * @return Options
     */
    virtual cxxopts::Options prepareOptions(const std::string& program) const;
 
..

Complex Example
===============

Here comes something big. Current implementations allows us to make complex parsing easily. Like

.. code:: bash

   program --help
   program create --help
   program create [create arguments]

..

The idea behind it is a little bit tricky, but it is working well enough.

So first of all you need 2 *.proto* files with own command settings, plain **program** and **program create**.

Here is main proto:

.. code:: plain

   syntax = "proto2";

   package bsw.protoargs.main;

   message protoargs
   {
       optional bool help = 1 [default = false];         // Print help and exit
       required string COMMAND = 2;                      // Command (create, copy, etc)
   }//protoargs

   message protoargs_links
   {
       optional string h = 11 [default = "help"];
       optional string help = 12 [default = "help"];
   }//protoargs

..

**Note**: Each of 2 proto files will be source for generated files, each generated set will have **class ProtoArgs** which will have name conflict, so change **package** directive, so that each command setting will be protected with own namespace.

So here we do expect no or single argument for main program. This limitation gives us advantage.

Let's go for the rest proto files

.. code:: plain

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

After generating all 8 files, let's think about these command parsing:

.. code:: bash

   program --help
   program create --help

..

For the first iteration we need to parse with main program parser. But it is created to parse the first and not the second. It will fail on **program create --help**. So as far as we have limited us to 2 options we may parse first 2 options only.

We still will be using **allowIncomplete** when parsing, to avoid error message saying *required parameter command is missing*, when searching for -h/--help.

.. code:: c++

    main::ProtoArgs arguments;

    // first time parse withh allowIncomplete to avoid missing required argument error
    auto config = std::unique_ptr<main::protoargs>( arguments.parse(program, argc < 2 ? argc : 2 /*need only 2 args to detect command*/, (char**)argv, true /*allow incomplete*/) );

    if (!config)
    {
       // you do not need usage output, it is already on the screen
       return EXIT_FAILURE;
    }

    if (argc == 1 || config->has_help()) // if no argument or --help specified print help end exit
    {
       std::cout << arguments.usage(program);
       return EXIT_SUCCESS;
    }

    // second time parse is full check parsing, so we do need this command
    config = std::unique_ptr<main::protoargs>( arguments.parse(program, argc < 2 ? argc : 2 /*need only 2 args to detect command*/, (char**)argv);

    if (!config)
    {
       // you do not need usage output, it is already on the screen
       return EXIT_FAILURE;
    }

    if (config->has_command && config->command() == "create")
    {
       ...
    }

    ...

..

Ok, we have discovered command, now that's time to parse. The only problem here is that we have positional argument (which is command) standing not at the end, so we can't create proper schema to parse. But as long as we found proper command we do not need it any more, so how about removing. So meet **exclude** method, which updates incoming arguments by removing some of them.

.. code:: c++

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

..

Now continue parsing our **create** command:

.. code:: c++

    ...

    if (config->has_command && config->command() == "create")
    {
         auto helpProgram = program + " " + command;

         main::create::ProtoArgs createArguments;

         auto filtered = createArguments.exclude(argc, (char**)argv, { 2 }); // remove 2nd position with command

         // first parsing - ignoring required parameters
         auto createConfig = std::unique_ptr<main::create::protoargs>( createArguments.parse(helpProgram, filtered.argc, filtered.argv, true /*allow incomplete*/) );

         if (!createConfig)
         {
            // you do not need usage output, it is already on the screen
            return EXIT_FAILURE;
         }

         if (argc == 1 || createConfig->has_help()) // if no argument or --help specified print help end exit
         {
            std::cout << createArguments.usage(helpProgram);
            return EXIT_SUCCESS;
         }

         // second full parsing with full check
         createConfig = std::unique_ptr<main::create::protoargs>( createArguments.parse(helpProgram, filtered.argc, filtered.argv, true /*allow incomplete*/) );

         if (!createConfig)
         {
            // you do not need usage output, it is already on the screen
            return EXIT_FAILURE;
         }

         // rest values discovery
         ...
    }

    ...

..

Extreme Usage
=============

Sometimes people need some real complex argument parsing, like

.. code:: bash

   program [program options] command [command options]

..

Well, I have not tested it this way, but you may achieve it. The trick is you need to calculate number of *[program options]* manually. This way you can exclude needed number of arguments, and proceed as previous example.

Building Tests
==============

Proceed to Tests_.

.. _Tests: src/Tests/
