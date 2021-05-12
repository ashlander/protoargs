import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""-r""",r"""--recursive""", help=r"""Recursive copy {OPTIONAL,type:bool,default:"false"}""", metavar=r"""recursive""", dest=r"""recursive"""   , action="store_const"  , const=(not False))

    parser.add_argument(r"""SRC""", type=str,  help=r"""Path to source path {REQUIRED,type:string}""")
    parser.add_argument(r"""DST""", type=str,  help=r"""Path to destination path {REQUIRED,type:string}""")

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
