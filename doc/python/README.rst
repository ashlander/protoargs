Description
===========

**Protoargs** is python proto file compiler, which generates arguments parser using argparse_.

This documentation part shows python parser generation and usage based on existing configuration. Start from main_ page for better description and proto file configuration rules.


.. _argparse: https://docs.python.org/3/library/argparse.html

.. _main: https://github.com/ashlander/protoargs/tree/master

**PROS**:

+ Creates python args parser using argparse_.
+ Simplifies creation even complex commands like 'command subcommand [subcommand_args]'

**CONS**:

- argparse_ is actually way more powerful
- Dependencies, not standalone (argparse_)

Usage
=====

.. image:: ../../src/Protoargs/img/pythonschema.png
   :align: center

First of all, you are interested in python script file in this project, python scripts are located in bin_ directory.

.. _bin: ../../src/Protoargs/bin/

.. code:: bash

   python protoargs.py -o <out DIR> -i PROTOFILE --py
               out DIR         [mandatory] path to output directory
               PROTOFILE       [mandatory] path to proto file

..

You should get 1 file as result: **_pa.py**. Attach it to your project and now you are ready to move forward.

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

    usage: schema [-h] [-a paramA] [--b-long-param paramB] [-c paramC]
                  [--d-long-param paramD] -e paramE [-f paramF [paramF ...]] [-i]
                  [--j-long] [-k paramFloat] [-l paramDouble]
                  PARAMG P_A_R_A_M_G_2 PARAM_FLOAT PARAM_DOUBLE PARAMH
                  [PARAMH ...]
 
    Test schema
 
    positional arguments:
      PARAMG                Positional integer param, positional param is always
                            \"required\" {REQUIRED,type:uint64}
      P_A_R_A_M_G_2         Positional boolean param, positional param is always
                            \"required\", Note: param set - true, missing - false
                            {REQUIRED,type:bool}
      PARAM_FLOAT           Positional float param {REQUIRED,type:float}
      PARAM_DOUBLE          Positional double param {REQUIRED,type:double}
      PARAMH                Positional repeating string params, there may be only
                            one repeating positional param {REQUIRED,type:string}
 
    optional arguments:
      -h, --help            show this help message and exit
      -a paramA, --a-long-param paramA
                            String param option with default value. Note: this
                            comment will be taken as description
                            {OPTIONAL,type:string,default:"// tricky default
                            value"}
      --b-long-param paramB
                            Integer param with default value
                            {OPTIONAL,type:uint32,default:"10"}
      -c paramC, --c-long-param paramC
                            Integer param without default value. Avoid new lines
                            they are rendered not correctly in help. Words will be
                            transfered to new line anyway
                            {OPTIONAL,type:int32,default:""}
      --d-long-param paramD
                            Float param without default value
                            {OPTIONAL,type:float,default:""}
      -e paramE             String param which should be anyway
                            {REQUIRED,type:string,default:""}
      -f paramF [paramF ...]
                            Integer param which may encounter multiple times
                            {REPEATED,type:int32,default:""}
      -i                    Boolean arg with default value (despite it is declared
                            after positional args, that is not a problem)
                            {OPTIONAL,type:bool,default:"true"}
      --j-long              Boolean arg without default value
                            {OPTIONAL,type:bool,default:""}
      -k paramFloat         Float param {OPTIONAL,type:float,default:""}
      -l paramDouble        Double param {OPTIONAL,type:double,default:""}

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

Now what you need is the file ending with **_pa.py**, it contains interface you need. It will look like several functions which you may use. Note: namespaces are not used currently.

**Note:** *-h/--help* arguments are predefined within the argparse_, so variant from proto file will be skipped, and warning message output

.. code:: python

   def usage(program, description="")

   def parse(program, description, argv, allowIncomplete=False)

..

They are quite clear, **usage** outputs help message, and the **parse** parses arguments. Both accept program name and description which you want to see in help, as long as **parse** method may call **usage** internally if something goes wrong.

**allowIncomplete** option if set to true, will return all successfully parsed arguments ignoring failed ones.

Let's go for code:

.. code:: python

   import sys
   import simple_pa

   class ArgsParser:

       def parse(self, argv):
           self.config = simple_pa.parse("schema", "Test schema", argv)

   if __name__ == "__main__":
       parser = ArgsParser()
       parser.parse(sys.argv[1:])
       print(parser.config)
       print(parser.p)
       ...

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

After generating all 3 files, let's think about these command parsing:

.. code:: bash

   program --help
   program create --help

..

For the first iteration we need to parse with main program parser. But it is created to parse the first and not the second. It will fail on **program create --help**. So as far as we have limited us to 2 options we may parse first 2 options only.

.. code:: python

   class ArgsParser:

       def parseCommand(self, argv):
           self.config = multy_command_pa.parse("program", "Useful multi command", argv)

   if __name__ == "__main__":
       parser = ArgsParser()

       parser.parseCommand(sys.argv[1:2])
       print(parser.config)

..

Ok, we have discovered command, now that's time to parse. The only problem here is that we have positional argument (which is command) standing not at the end, so we can't create proper schema to parse. But as long as we found proper command we do not need it any more, so how about removing it from arguments.

.. code:: python

   class ArgsParser:

       def parseCommand(self, argv):
           self.config = multy_command_pa.parse("program", "Useful multi command", argv)

       def parseCreate(self, argv):
           self.config = multy_command_create_pa.parse("program create", "Useful create", argv)

       def parseCopy(self, argv):
           self.config = multy_command_copy_pa.parse("program copy", "Useful copy", argv)

   if __name__ == "__main__":
       parser = ArgsParser()

       parser.parseCommand(sys.argv[1:2])
       print(parser.config)

       if (parser.config.COMMAND == "create"):
           parser.parseCreate(sys.argv[2:])
       elif (parser.config.COMMAND == "copy"):
           parser.parseCopy(sys.argv[2:])
       else:
           sys.exit(1)
       print(parser.config)

..

Extreme Usage
=============

Sometimes people need some real complex argument parsing, like

.. code:: bash

   program [program options] command [command options]

..

Well, I have not tested it this way, but you may achieve it. The trick is you need to calculate number of *[program options]* manually. This way you can exclude needed number of arguments, and proceed as previous example.

