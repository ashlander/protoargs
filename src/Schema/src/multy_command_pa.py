import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)


    parser.add_argument(r"""COMMAND""", type=str,  help=r"""Command (create, copy) {REQUIRED,type:string}""")

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
