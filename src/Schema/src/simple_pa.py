import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""--count""", required=True, help=r"""Converted to --count {REQUIRED,type:uint64,default:"1"}""", metavar=r"""count""", dest=r"""count""" , type=int   , default=1 )
    parser.add_argument(r"""--configuration""", help=r"""Converted to --configuration {OPTIONAL,type:string,default:""}""", metavar=r"""configuration""", dest=r"""configuration""" , type=str    )
    parser.add_argument(r"""--flags""", help=r"""Converted to --flags, each encounter will be stored in list {REPEATED,type:bool,default:""}""", metavar=r"""flags""", dest=r"""flags"""  , nargs="?" , action="append"  , const=True)
    parser.add_argument(r"""--version""", help=r"""Converted to --version {OPTIONAL,type:bool,default:"false"}""", metavar=r"""version""", dest=r"""version"""   , action="store_const"  , const=(not False))
    parser.add_argument(r"""-c""", help=r"""Converted to -c short option {OPTIONAL,type:string,default:"some value"}""", metavar=r"""c""", dest=r"""c""" , type=str   , default=r"""some value""" )


    return parser

def usage(program, description=""):
    return prepareOptions(program, description).format_help()

def parse(program, description, argv, allowIncomplete=False):

    parser = prepareOptions(program, description)

    args = None
    if allowIncomplete:
        args = parser.parse_known_args(argv)
    else:
        args = parser.parse_args(argv)

    return args;
