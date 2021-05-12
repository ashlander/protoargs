import argparse


def prepareOptions(program, description):

    parser = argparse.ArgumentParser(description=description, prog=program)

    parser.add_argument(r"""-a""",r"""--a-long-param""", help=r"""String param option with default value. Note: this comment will be taken as description {OPTIONAL,type:string,default:"// tricky default value"}""", metavar=r"""paramA""", dest=r"""paramA""" , type=str   , default=r"""// tricky default value""" )
    parser.add_argument(r"""--b-long-param""", help=r"""Integer param with default value {OPTIONAL,type:uint32,default:"10"}""", metavar=r"""paramB""", dest=r"""paramB""" , type=int   , default=10 )
    parser.add_argument(r"""-c""",r"""--c-long-param""", help=r"""Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway {OPTIONAL,type:int32,default:""}""", metavar=r"""paramC""", dest=r"""paramC""" , type=int    )
    parser.add_argument(r"""--d-long-param""", help=r"""Float param without default value {OPTIONAL,type:float,default:""}""", metavar=r"""paramD""", dest=r"""paramD""" , type=float    )
    parser.add_argument(r"""-e""", required=True, help=r"""String param which should be anyway {REQUIRED,type:string,default:""}""", metavar=r"""paramE""", dest=r"""paramE""" , type=str    )
    parser.add_argument(r"""-f""", help=r"""Integer param which may encounter multiple times {REPEATED,type:int32,default:""}""", metavar=r"""paramF""", dest=r"""paramF""" , type=int , nargs="+" , action="append"  )
    parser.add_argument(r"""-i""", help=r"""Boolean arg with default value (despite it is declared after positional args, that is not a problem) {OPTIONAL,type:bool,default:"true"}""", metavar=r"""param_I""", dest=r"""param_I"""   , action="store_const"  , const=(not True))
    parser.add_argument(r"""--j-long""", help=r"""Boolean arg without default value {OPTIONAL,type:bool,default:""}""", metavar=r"""param_J""", dest=r"""param_J"""   , action="store_const"  , const=True)
    parser.add_argument(r"""-k""", help=r"""Float param {OPTIONAL,type:float,default:""}""", metavar=r"""paramFloat""", dest=r"""paramFloat""" , type=float    )
    parser.add_argument(r"""-l""", help=r"""Double param {OPTIONAL,type:double,default:""}""", metavar=r"""paramDouble""", dest=r"""paramDouble""" , type=float    )

    parser.add_argument(r"""PARAMG""", type=int,  help=r"""Positional integer param, positional param is always \"required\" {REQUIRED,type:uint64}""")
    parser.add_argument(r"""P_A_R_A_M_G_2""", type=bool,  help=r"""Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false {REQUIRED,type:bool}""")
    parser.add_argument(r"""PARAM_FLOAT""", type=float,  help=r"""Positional float param {REQUIRED,type:float}""")
    parser.add_argument(r"""PARAM_DOUBLE""", type=float,  help=r"""Positional double param {REQUIRED,type:double}""")
    parser.add_argument(r"""PARAMH""", type=str, nargs="+", help=r"""Positional repeating string params, there may be only one repeating positional param {REQUIRED,type:string}""")

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
