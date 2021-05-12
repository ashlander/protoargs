import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""-i""", required=True, help=r"""Path to proto file with protoargs configuration {REQUIRED,type:string,default:""}""", metavar=r"""src""", dest=r"""src""" , type=str    )
    parser.add_argument(r"""-o""", required=True, help=r"""Path to output directory, where parser will be placed. {REQUIRED,type:string,default:""}""", metavar=r"""dst""", dest=r"""dst""" , type=str    )
    parser.add_argument(r"""--loglevel""", help=r"""Log level, default = INFO, possible values [ERROR|WARNING|INFO|DEBUG] {OPTIONAL,type:string,default:"INFO"}""", metavar=r"""loglevel""", dest=r"""loglevel""" , type=str   , default=r"""INFO""" )
    parser.add_argument(r"""--cpp""", help=r"""Generate c++11 arguments parser (Note: you need generate files with protoc compiler additionally, so that parser will work). Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs.pa.cc] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""cpp""", dest=r"""cpp"""   , action="store_const"  , const=(not False))
    parser.add_argument(r"""--py""", help=r"""Generate python arguments parser. Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs_pa.py] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""py""", dest=r"""py"""   , action="store_const"  , const=(not False))


    return parser

def usage(program, description=""):
    return prepareOptions(program, description).format_help()

def parse(program, description, argv, allowIncomplete=False):

    parser = prepareOptions(program, description)

    args = parser.parse_args(argv)

    return args;
