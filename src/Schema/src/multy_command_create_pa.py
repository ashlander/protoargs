import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""-s""",r"""--size""", help=r"""Size of the file {OPTIONAL,type:uint64,default:"0"}""", metavar=r"""size""", dest=r"""size""" , type=int   , default=0 )

    parser.add_argument(r"""PATH""", type=str,  help=r"""Path to file to create {REQUIRED,type:string}""")

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
