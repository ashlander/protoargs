import os
import logging
import paTokenizer


# GLOBAL DEFS ###################################3

#class ProtoTypes:
pt_float = "float"
pt_double = "double"
pt_int32 = "int32"
pt_uint32 = "uint32"
pt_int64 = "int64"
pt_uint64 = "uint64"
pt_bool = "bool"
pt_string = "string"

# python types
py_float = "float"
py_double = "float"
py_int32 = "int"
py_uint32 = "int"
py_int64 = "int"
py_uint64 = "int"
py_bool = "bool"
py_string = "str"

# END GLOBALS ###################################3

class Generator:

    __path = "" # path to proto file
    __pyPath = "" # path to source file
    __py = "" # source file content

    def __init__(self, path, dst):
        self.__path = path
        filename = os.path.splitext( os.path.basename(path) )[0]
        base = os.path.join(dst, filename)
        self.__pyPath = base + "_pa.py"

    def getSourceFileData(self):
        return self.__py

    def getSourceFilePath(self):
        return self.__pyPath

    # load file entirely
    def loadFileData(self, path):
        logging.info("Load file: '" + path + "'")
        try:
            with open(path, "r") as index:
                lines = index.readlines()
                index.close()
                return lines
        except:
            logging.error("Could not read file '" + path + "' because of error")
            return ""

    def __saveFileData(self, path, data):
        logging.info("Save file: '" + path + "'")
        try:
            with open(path, "w") as index:
                index.write(data)
                index.close()
                return True;
        except:
            logging.error(" Could not write to file '" + path + "' because of error")
            return False;

    # parse proto file and generate python files
    def generate(self):
        #load proto file
        data = self.loadFileData(self.__path)
        result = len(data) != 0
        if result:
            # tokenize proto file data
            tokenizer = paTokenizer.Tokenizer() \
                    .tokenize(data) \
                    .excludeUnused() \

            result = tokenizer.check() # check tokens
            if result:
                tokens = tokenizer.getTokens()

                # DBG
                for token in tokens:
                    logging.debug(str(token))

                # generate souce code
                self.__py = self.__generateSourceFromTokens(tokens)

                # save code to files
                self.__saveFileData( self.getSourceFilePath(), self.__py )

        return data

    # convert protobuf config names into c code names
    def __convertToPyName(self, name):
        return name.lower()

    # convert protobuf config names into args
    def __convertToArgName(self, name):
        return name.replace("_","-")

    # convert argument to option
    def __convertToOptName(self, name):
        if len(name) == 1:
            return "-" + name
        elif len(name) > 1:
            return "--" + name
        else:
            return name

    # convert protobuf config types into python types
    def __convertToPyType(self, token):
        pyType = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            pyType = py_int32
        if protoType == pt_uint32:
            pyType = py_uint32
        if protoType == pt_int64:
            pyType = py_int64
        if protoType == pt_uint64:
            pyType = py_uint64
        if protoType == pt_bool:
            pyType = py_bool
        if protoType == pt_string:
            pyType = py_string
        if protoType == pt_float:
            pyType = py_float
        if protoType == pt_double:
            pyType = py_double

        return pyType

    def __convertToDefaultValue(self, token):
        if not token.value:
            return ""
        return (r'r"""' + token.value + r'"""' if token.type == pt_string else token.value).replace("true", "True").replace("false", "False")

    # generate python source file content
    def __generateSourceFromTokens(self, tokens):
        head = """import argparse\n
"""

        tail = ""
        body = ""
        prefix = ""
        for token in tokens:
            if token.directive == paTokenizer.pd_package:
                logging.debug(str(token))
                namespaces = token.name.split(".") #discover namespaces
                prefix = "_".join(namespaces)

        # add prepareOptions function binding
        body += """
def prepareOptions(program, description):
"""
        # register arguments
        body += self.__cxxoptsProgramDescription(tokens)

        body += self.__cxxoptsProgramOptions(tokens)

        body += self.__cxxoptsPositionalOptions(tokens)

        body += """
    return parser
"""


        # add usage function binding
        body += """
def usage(program, description=""):
    return prepareOptions(program, description).format_help()
"""

        # add prepareOptions function binding
        body += """
def parse(program, description, argv, allowIncomplete=False):
"""
        # add arguments parsing using cxxopts
        body += self.__cxxoptsParsingBegin(tokens)

        body += """
    return args;
"""

        return head + body + tail

    # get token by type and name
    def __getToken(self, tokens, directive, name):
        result = paTokenizer.ProtoToken()
        for token in tokens:
            if token.directive == directive and token.name == name:
                result = token
                break
        return result

    # get link tokens by field name
    def __getLinks(self, tokens, name):
        result = []
        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_links:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field and token.value == name: # default link value should be the name of args
                    result.append(token)
        return result


    def __cxxoptsProgramDescription(self, tokens):
        code = """
    parser = argparse.ArgumentParser(description=description, prog=program)
"""
        token = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_main)
        if token.valid():
            code = code.replace("%DESCRIPTION%", token.description)

        code += "\n"
        return code

    def __cxxoptsPositionalOptions(self, tokens):
        template = r'parser.add_argument(r"""%OPTIONS%""", type=%TYPE%, %NARGS% help=r"""%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}""")'
        code = ""
        positional = []

        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) == 0:
                            positional.append(token)

        # add positional long args
        for token in positional:
            logging.debug("Create positional field name: " + str(token))
            code += "    "
            code += template \
                    .replace("%OPTIONS%", token.name) \
                    .replace("%DESCRIPTION%", token.description) \
                    .replace("%PTYPE%", token.type) \
                    .replace("%TYPE%", self.__convertToPyType(token)) \
                    .replace("%ARGNAME%", token.name) \
                    .replace("%FREQUENCY%", paTokenizer.pf_required.upper()) \
                    .replace("%NARGS%", (r'nargs="+",' if token.field == paTokenizer.pf_repeated else "") )

            code += "\n"

        return code

    def __cxxoptsProgramOptions(self, tokens):
        template = r'parser.add_argument(r"""%OPTIONS%""", help=r"""%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:"%DEFAULT%"}""", metavar=r"""%ARGNAME%""", dest=r"""%ARGNAME%""" %TYPE% %NARGS% %ACTIONS% %DEFAULTVAL% %CONST%)'
        templateRequired = r'parser.add_argument(r"""%OPTIONS%""", required=True, help=r"""%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:"%DEFAULT%"}""", metavar=r"""%ARGNAME%""", dest=r"""%ARGNAME%""" %TYPE% %NARGS% %ACTIONS% %DEFAULTVAL% %CONST%)'
        code = ""
        positional = []

        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:

                    # set template
                    t = template
                    if token.field == paTokenizer.pf_required:
                        t = templateRequired

                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) > 0:
                            # add all links as options
                            logging.debug("links found for: " + str(token) + "\n" + str(links))
                            options = ""
                            for link in links:
                                if link.name != "h" and link.name != "help": # exclude predefined args
                                    if options:
                                        options += r'""",r"""'
                                    options += self.__convertToOptName( self.__convertToArgName(link.name) ) # convert into args
                                else:
                                    logging.warn("'" + link.name + "' conflicts with predefined argument");

                            if options:
                                code += "    "
                                code += t \
                                        .replace("%OPTIONS%",options) \
                                        .replace("%DESCRIPTION%",token.description) \
                                        .replace("%PTYPE%", token.type) \
                                        .replace("%ARGNAME%", token.name) \
                                        .replace("%FREQUENCY%", token.field.upper()) \
                                        .replace("%DEFAULT%", token.value) \
                                        .replace("%TYPE%", \
                                        (", type=" + self.__convertToPyType(token) if token.type != pt_bool else "") ) \
                                        .replace("%DEFAULTVAL%", \
                                        (", default=" + self.__convertToDefaultValue(token) if token.value and token.type != pt_bool else "") ) \
                                        .replace("%NARGS%", \
                                        (r', nargs="+"' if token.field == paTokenizer.pf_repeated else "") ) \
                                        .replace("%ACTIONS%", \
                                        (r', action="append"' if token.field == paTokenizer.pf_repeated else \
                                        (r', action="store_const"' if token.type == pt_bool else "")) ) \
                                        .replace("%CONST%", \
                                        (r', const=(not ' + self.__convertToDefaultValue(token) + ")" if token.type == pt_bool and token.value else \
                                        (r', const=True' if token.type == pt_bool else "")) ) \

                                code += "\n"
                        else:
                            logging.debug("positional arg found: " + str(token))
                            positional.append(token)
                    else:
                        logging.debug("convert main protoargs field name into long arg name: " + str(token))
                        code += "    "
                        code += t \
                                .replace("%OPTIONS%", self.__convertToOptName( self.__convertToArgName(token.name)) ) \
                                .replace("%DESCRIPTION%",token.description) \
                                .replace("%PTYPE%", token.type) \
                                .replace("%ARGNAME%", token.name) \
                                .replace("%FREQUENCY%", token.field.upper()) \
                                .replace("%DEFAULT%", token.value) \
                                .replace("%TYPE%", \
                                (", type=" + self.__convertToPyType(token) if token.type != pt_bool else "") ) \
                                .replace("%DEFAULTVAL%", \
                                (", default=" + self.__convertToDefaultValue(token) if token.value and token.type != pt_bool else "") ) \
                                .replace("%NARGS%", \
                                (r', nargs="+"' if token.field == paTokenizer.pf_repeated else "") ) \
                                .replace("%ACTIONS%", \
                                (r', action="append"' if token.field == paTokenizer.pf_repeated else \
                                (r', action="store_const"' if token.type == pt_bool else "")) ) \
                                .replace("%CONST%", \
                                (r', const=(not ' + self.__convertToDefaultValue(token) + ")" if token.type == pt_bool and token.value else \
                                (r', const=True' if token.type == pt_bool else "")) ) \

                        code += "\n"
                else:
                    logging.warn("unknown token inside protoargs structure: " + str(token))

        code += "\n"
        return code

    def __cxxoptsParsingBegin(self, tokens):
        code = """
    parser = prepareOptions(program, description)
"""
        # add cxxopts parsing
        code += """
    args = parser.parse_args(argv)
"""
        return code

