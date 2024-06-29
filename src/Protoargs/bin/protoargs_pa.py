import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""-i""" , type=str, required=True, help=r"""Path to proto file with protoargs configuration {REQUIRED,type:string,default:""}""", metavar=r"""src""", dest=r"""src"""    )
    parser.add_argument(r"""-o""" , type=str, required=True, help=r"""Path to output directory, where parser will be placed. {REQUIRED,type:string,default:""}""", metavar=r"""dst""", dest=r"""dst"""    )
    parser.add_argument(r"""--loglevel""" , type=str, help=r"""Log level, possible values [ERROR|WARNING|INFO|DEBUG] {OPTIONAL,type:string,default:"INFO"}""", metavar=r"""loglevel""", dest=r"""loglevel"""   , default=r"""INFO""" )
    parser.add_argument(r"""--cpp""" , help=r"""Generate c++11 arguments parser (Note: you need generate files with protoc compiler additionally, so that parser will work). Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs.pa.cc] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""cpp""", dest=r"""cpp"""  , action="store_const" , default=False , const=True)
    parser.add_argument(r"""--py""" , help=r"""Generate python arguments parser. Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs_pa.py] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""py""", dest=r"""py"""  , action="store_const" , default=False , const=True)
    parser.add_argument(r"""--rust""" , help=r"""Generate rust arguments parser. Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs_pa.rs] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""rust""", dest=r"""rust"""  , action="store_const" , default=False , const=True)
    parser.add_argument(r"""--go""" , help=r"""Generate go arguments parser. Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs_pa.go] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""go""", dest=r"""go"""  , action="store_const" , default=False , const=True)
    parser.add_argument(r"""--bash""" , help=r"""Generate bash arguments parser. Parser will have name of proto file name, e.g. [protoargs.proto]->[protoargs_pa.sh] {OPTIONAL,type:bool,default:"false"}""", metavar=r"""bash""", dest=r"""bash"""  , action="store_const" , default=False , const=True)


    return parser

def usage(program, description=""):
    return prepareOptions(program, description).format_help()

def parse(program, description, argv, known=False):

    parser = prepareOptions(program, description)

    args = None
    if known:
        args, _ = parser.parse_known_args(argv)
    else:
        args = parser.parse_args(argv)

    return args;
