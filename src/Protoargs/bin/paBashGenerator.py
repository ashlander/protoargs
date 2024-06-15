import os
import sys
import logging
import paTokenizer
import paPyGenerator

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

# go types
bash_float = "float32"
bash_double = "float64"
bash_int32 = "int32"
bash_uint32 = "uint32"
bash_int64 = "int64"
bash_uint64 = "uint64"
bash_bool = "bool"
bash_string = "string"

# END GLOBALS ###################################3

class Generator:

    __path = "" # path to proto file
    __package = "" # package to avoid global variables collisions
    __bashCommonPath = "" # path to common source file
    __bashPath = "" # path to source file
    __bash = "" # source file content

    def __init__(self, path, dst):
        self.__path = path
        filename = os.path.splitext( os.path.basename(path) )[0]
        self.__package = self.__convertToPackageName(filename)
        base = os.path.join(dst, filename)
        self.__bashCommonPath = os.path.join(dst, "protoargs.sh")
        self.__bashPath = base + "_pa.sh"

    ##
    # @brief Additionally generate python parser and steal usage from it
    # Simple enough, dumb enough, but it works
    # @param path
    #
    # @return 
    def __parasiteUsage(self, path):
        filename = os.path.splitext( os.path.basename(path) )[0]
        dstdir = os.path.join("/", "tmp")
        logging.info("Generate python parser from proto file '" + path + "'")
        generator = paPyGenerator.Generator(path, dstdir)
        generator.generate()

        # import generated module dynamically
        sys.path.append(dstdir)
        module = __import__(filename + "_pa")
        os.environ['COLUMNS']="80" # make default limit in 80 columns

        # TODO escape '"' char
        return module.usage("${program}", "${description}")

    def getSourceFileData(self):
        return self.__bash

    def getSourceFilePath(self):
        return self.__bashPath

    def getCommonFilePath(self):
        return self.__bashCommonPath

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

    # parse proto file and generate go files
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
                self.__bash = self.__generateSourceFromTokens(tokens)

                # save code to files
                self.__saveFileData( self.getSourceFilePath(), self.__bash )

        return data

    # convert protobuf config names into go code names
    def __convertToPackageName(self, name):
        return name \
                .replace(".", "_") \
                .replace(" ", "_")

    # convert protobuf config names into bash code names
    def __convertToBashName(self, name):
        return self.__package + "_"+ name

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

    # convert protobuf config types into go types
    def __convertToGoType(self, token):
        pyType = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            pyType = bash_int32
        if protoType == pt_uint32:
            pyType = bash_uint32
        if protoType == pt_int64:
            pyType = bash_int64
        if protoType == pt_uint64:
            pyType = bash_uint64
        if protoType == pt_bool:
            pyType = bash_bool
        if protoType == pt_string:
            pyType = bash_string
        if protoType == pt_float:
            pyType = bash_float
        if protoType == pt_double:
            pyType = bash_double

        return pyType

    def __convertToDefaultValue(self, token):
        if not token.value:
            return ""
        return (r'r"""' + token.value + r'"""' if token.type == pt_string else token.value).replace("true", "True").replace("false", "False")

    # generate go source file content
    def __generateSourceFromTokens(self, tokens):
        head = "#!/bin/bash\n"
        tail = ""
        body = ""

        # add prepare_options function binding
        body += """
# Options preparation
function %PACKAGE%_prepareOptions()
{
    # Common Variables
    %PACKAGE%_PROTOARG_USAGE=""
"""
        # init variables
        body += self.__flagStructureFields(tokens)

        body += """

}
"""

        # add usage function binding
        body += r"""
# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function %PACKAGE%_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    %PACKAGE%_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
"""

        body += self.__parasiteUsage(self.__path)

        # register usage arguments
        #body += self.__flagProgramUsage(tokens)

        body += r"""
PROTOARGS_EOM
)"
}

"""

        body += """
# Parse command line arguments, and return filled configuration
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
# * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
# wrong type cast will produce error anyway
# * `args` - Command line arguments, use $@ to pass them
#
# returns Result with configuration structure, or error message
function %PACKAGE%_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    %PACKAGE%_prepareOptions
    %PACKAGE%_usage "${program}" "${description}"

"""

        # register fields
        body += self.__addParsing(tokens)

        # verify fields
        body += self.__flagStructureFill(tokens)

        body += r"""
    return 0
}

"""

        return (head + body + tail).replace("%PACKAGE%", self.__package)

    def __addParsing(self, tokens):
        templateDefault = r"""
            %ARGUMENT%)
                local value=$2
                if %CHECKER%; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected '%OPTION%' of type %TYPE% but the value is '${value}'"
                        echo "${%PACKAGE%_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    %NAME%=$2
                fi
                %NAME_PRESENT%=true
                shift # past argument
                shift # past value
                ;;
"""

        templateDefaultRepeated = r"""
            %ARGUMENT%)
                local value=$2
                if %CHECKER%; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected '%OPTION%' of type %TYPE% but the value is '${value}'"
                        echo "${%PACKAGE%_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    %NAME%+=("$2")
                fi
                %NAME_PRESENT%=true
                %NAME%_COUNT=$((%NAME%_COUNT + 1))
                shift # past argument
                shift # past value
                ;;
"""

        templateString = r"""
            %ARGUMENT%)
                %NAME%="$2"
                %NAME_PRESENT%=true
                shift # past argument
                shift # past value
                ;;
"""


        templateBool = r"""
            %ARGUMENT%)
                %NAME%=true
                %NAME_PRESENT%=true
                shift
                ;;
"""

        templateDefaultEquals = r"""
            %ARGUMENT%)
                local value="${1#*=}"
                if %CHECKER%; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected '%OPTION%' of type %TYPE% but the value is '${value}'"
                        echo "${%PACKAGE%_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    %NAME%="${1#*=}"
                fi
                %NAME_PRESENT%=true
                shift # past argument=value
                ;;
"""

        templateStringEquals = r"""
            %ARGUMENT%)
                %NAME%="${1#*=}"
                %NAME_PRESENT%=true
                shift # past argument=value
                ;;
"""


        templateDefaultRepeatedEquals = r"""
            %ARGUMENT%)
                local value="${1#*=}"
                if %CHECKER%; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected '%OPTION%' of type %TYPE% but the value is '${value}'"
                        echo "${%PACKAGE%_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    %NAME%+=("${1#*=}")
                fi
                %NAME_PRESENT%=true
                %NAME%_COUNT=$((%NAME%_COUNT + 1))
                shift # past argument=value
                ;;
"""


        code = """
    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in
"""

        positionals = 0
        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    append = True
                    positional = False
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    argument = self.__convertToArgName(token.name)
                    argument_eq = argument + "=*"
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) == 0:
                            positional = True
                        else:
                            argument = ""
                            argument_eq = ""
                            for link in links:
                                arg = self.__convertToArgName(link.name)
                                arg = ("-" + arg if len(arg) <= 1 else "--" + arg)
                                if argument:
                                    argument += "|" + arg
                                    argument_eq += "|" + arg + "=*"
                                else:
                                    argument = arg
                                    argument_eq = arg + "=*"
                    else:
                        argument = ("-" + argument if len(argument) <= 1 else "--" + argument)
                        argument_eq = argument + "=*"

                    if append:
                        bashType = self.__convertToGoType(token)

                        # count positionals expected
                        if positional:
                            positionals += 1

                        if not positional:
                            logging.debug("Add field name processing: " + str(token))
                            template_eq = templateDefaultEquals
                            template = templateDefault
                            if token.type == pt_bool:
                                template = templateBool
                                if token.field != paTokenizer.pf_repeated:
                                    template_eq = "" # no = for flag, like --help
                                else:
                                    template = "" # no boolean repeated without =
                                    template_eq = templateDefaultRepeatedEquals
                            elif token.type == pt_string:
                                template = templateString
                                template_eq = templateStringEquals
                                if token.field == paTokenizer.pf_repeated:
                                    template = templateDefaultRepeated
                                    template_eq = templateDefaultRepeatedEquals

                            # argument with space
                            code += template \
                                    .replace("%NAME%", self.__convertToBashName(token.name)) \
                                    .replace("%NAME_PRESENT%", self.__convertToBashName(token.name) + "_PRESENT") \
                                    .replace("%TYPE%", bashType) \
                                    .replace("%ARGUMENT%", argument) \
                                    .replace("%OPTION%", self.__convertToArgName(token.name)) \

                            # argument with '='
                            code += template_eq \
                                    .replace("%NAME%", self.__convertToBashName(token.name)) \
                                    .replace("%NAME_PRESENT%", self.__convertToBashName(token.name) + "_PRESENT") \
                                    .replace("%TYPE%", bashType) \
                                    .replace("%ARGUMENT%", argument_eq) \
                                    .replace("%OPTION%", self.__convertToArgName(token.name)) \

                            # checker
                            code = code.replace("%CHECKER%", ( \
                                    r"""[ "${value}" != true ] && [ "${value}" != false ]""" if token.type == pt_bool \
                                    else r"""! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]]"""  if token.type == pt_double or token.type == pt_float \
                                    else r"""! [[ "${value}" =~ ^[+-][0-9]+$ ]]"""  if token.type == pt_int32 or token.type == pt_int64 \
                                    else r"""! [[ "${value}" =~ ^[0-9]+$ ]]"""  if token.type == pt_uint32 or token.type == pt_uint64 \
                                    else r"""[ "0" -ne "0" ]""" \
                                    )) \

        code += """
            -*|--*)
                echo "[ERR] Unknown option '$1'"
                echo "${%PACKAGE%_PROTOARG_USAGE}"
                return 1
                ;;
            *)
                POSITIONAL_ARGS+=("$1") # save positional arg
                shift # past argument
                ;;
        esac
    done

    set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

"""

        templatePositionalDefault = r"""
    if [ "$allow_incomplete" == false ] && [ %POSITION% -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "Positional '%TRUENAME%' parameter is not set"
        return 1
    fi
    %NAME%="${POSITIONAL_ARGS[%POSITION%]}"
    %NAME%_PRESENT=true
"""

        position = 0
        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    append = True
                    positional = False
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    argument = self.__convertToArgName(token.name)
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) == 0:
                            positional = True
                            position += 1

                    if append:
                        bashType = self.__convertToGoType(token)

                        if positional:
                            logging.debug("Fill positional name: " + str(token))
                            template = templatePositionalDefault
                            code += template \
                                    .replace("%NAME%", self.__convertToBashName(token.name)) \
                                    .replace("%TRUENAME%", token.name) \
                                    .replace("%POSITION%", str(position-1)) \
                                    .replace("%ARGUMENT%", argument) \

        return code

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

    def __flagStructureFields(self, tokens):
        templateDefault = """
    # %DESCRIPTION%
    %NAME%=%DEFAULTVAL%
    %NAME%_PRESENT=false\n"""

        templateRepeated = """
    # %DESCRIPTION%
    %NAME%=%DEFAULTVAL%
    %NAME%_PRESENT=false
    %NAME%_COUNT=0\n"""

        code = ""

        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    logging.debug("Create struct field name: " + str(token))
                    template = templateDefault
                    if token.field == paTokenizer.pf_repeated:
                        template = templateRepeated
                    code += template \
                            .replace("%NAME%", self.__convertToBashName(token.name)) \
                            .replace("%DESCRIPTION%", token.description) \
                            .replace("%DEFAULTVAL%", \
                            ("()" if token.field == paTokenizer.pf_repeated \
                            else "\"" + token.value + "\"" if token.type == pt_string \
                            else "false" if len(token.value) == 0 and token.type == pt_bool \
                            else "0" if len(token.value) == 0 else token.value) ) \

        return code

    def __flagStructureFill(self, tokens):
        templateOptional = r""""""


        templateOptionalBool = r""""""

        templateRequired = r"""
    if [ "$allow_incomplete" == false ] && [ $%NAME%_PRESENT == false ]; then
        echo "[ERR] Required '%OPTION%' is missing"
        echo "${%PACKAGE%_PROTOARG_USAGE}"
        return 1
    fi
"""

        templateRepeated = r""""""

        templatePositional = r""""""

        templateRepeatedPositional = r"""
        # repeated positional
        if !allow_incomplete && flags.NArg() < %POSITION% {
        err%NAME% := errors.New(`Required at least one positional '%OPTION%'`)
        fmt.Println(err%NAME%)
        fmt.Println(Usage(program, description))
        return config, err%NAME%
    }
    for i := %INDEX%; i < flags.NArg(); i++ {
        err%NAME% := %VARIABLE%.Set(flags.Arg(i))
        if !allow_incomplete && err%NAME% != nil {
            fmt.Println(err%NAME%)
            fmt.Println(Usage(program, description))
            return config, err%NAME%
        }
    }
"""
        code = ""
        position = 0

        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    append = True
                    positional = False
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    argument = self.__convertToArgName(token.name)
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) == 0:
                            positional = True
                        else:
                            argument = self.__convertToArgName(links[0].name)

                    if append:
                        logging.debug("Fill struct field name: " + str(token))
                        bashType = self.__convertToGoType(token)

                        if positional:
                            position += 1

                        template = templateOptional
                        if positional and token.field == paTokenizer.pf_repeated:
                            template = templateRepeatedPositional
                        elif positional:
                            template = templatePositional
                        elif token.field == paTokenizer.pf_optional and token.type == pt_bool:
                            template = templateOptionalBool
                        elif token.field == paTokenizer.pf_required and token.type == pt_bool:
                            template = templateOptionalBool + templateRequired
                        elif token.field == paTokenizer.pf_repeated:
                            template = templateRepeated
                        elif token.field == paTokenizer.pf_required:
                            template = templateRequired

                        code += template \
                                .replace("%NAME%", self.__convertToBashName(token.name)) \
                                .replace("%ARGUMENT%", argument) \
                                .replace("%OPTION%", self.__convertToArgName(token.name)) \
                                .replace("%TYPE%", bashType) \
                                .replace("%VARIABLE%", "config." + self.__convertToBashName(token.name)) \
                                .replace("%POSITION%", str(position)) \
                                .replace("%INDEX%", str(position-1))

        return code

    def __flagInitConfig(self, tokens):
        template = """    config.%NAME% = %TYPE%{%DEFAULTVAL%, false}\n"""

        code = """
    config := new(Config)
"""

        start = False
        for token in tokens:
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    append = True
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    #if isLinks:
                    #    links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                    #    for link in links:
                    #        if link.name == "h" or link.name == "help": # exclude predefined args
                    #            append = False
                    #            break

                    if append:
                        logging.debug("Create struct field name: " + str(token))
                        bashType = self.__convertToGoType(token)
                        if token.field == paTokenizer.pf_repeated:
                            bashType = "Array" + bashType.capitalize() + "Flags"
                        elif token.field == paTokenizer.pf_optional:
                            bashType = bashType.capitalize() + "Value"
                        elif token.field == paTokenizer.pf_required:
                            bashType = bashType.capitalize() + "Value"

                        if token.field != paTokenizer.pf_repeated:
                            code += template \
                                    .replace("%NAME%", self.__convertToBashName(token.name)) \
                                    .replace("%TYPE%", bashType) \
                                    .replace("%DESCRIPTION%", token.description) \
                                    .replace("%DEFAULTVAL%", \
                                    ("`" + token.value + "`" if token.type == pt_string else "false" if len(token.value) == 0 and token.type == pt_bool else "0" if len(token.value) == 0 else token.value) ) \

        return code

    def __flagProgramOptions(self, tokens):
        templateOptional = r"""
    flags.Var(&%VARIABLE%, `%OPTIONS%`, `%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:%DEFAULT%}`)"""
        templateRequired = r"""
    flags.Var(&%VARIABLE%, `%OPTIONS%`, `%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}`)"""
        templateRepeated = r"""
    flags.Var(&%VARIABLE%, `%OPTIONS%`, `%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}`)"""
        templateOptionalBool = r"""
    flags.BoolVar(&%VARIABLE%.val, `%OPTIONS%`, %DEFAULT%, `%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:%DEFAULT%}`)"""
        templateRequiredBool = r"""
    flags.BoolVar(&%VARIABLE%.val, `%OPTIONS%`, %DEFAULT%, `%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}`)"""

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
                    t = templateOptional
                    if token.field == paTokenizer.pf_required and token.type == pt_bool:
                        t = templateRequiredBool
                    elif token.field == paTokenizer.pf_optional and token.type == pt_bool:
                        t = templateOptionalBool
                    elif token.field == paTokenizer.pf_required:
                        t = templateRequired
                    elif token.field == paTokenizer.pf_repeated:
                        t = templateRepeated

                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) > 0:
                            # add all links as options
                            logging.debug("links found for: " + str(token) + "\n" + str(links))
                            for link in links:
                                code += t \
                                        .replace("%OPTIONS%", self.__convertToArgName(link.name)) \
                                        .replace("%DESCRIPTION%",token.description) \
                                        .replace("%PTYPE%", token.type) \
                                        .replace("%ARGNAME%", token.name) \
                                        .replace("%FREQUENCY%", token.field.upper()) \
                                        .replace("%DEFAULT%", \
                                        ("\"" + token.value + "\"" if token.type == pt_string else "false" if len(token.value) == 0 and token.type == pt_bool else "0" if len(token.value) == 0 else token.value) ) \
                                        .replace("%TYPE%", \
                                        (", type=" + self.__convertToGoType(token) if token.type != pt_bool else "") ) \
                                        .replace("%REQUIRED%", \
                                        ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                        .replace("%REPEATED%", \
                                        ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                        .replace("%WITHVALUE%", \
                                        ("true" if token.type != pt_bool else "false") ) \
                                        .replace("%VARIABLE%", "config." + self.__convertToBashName(token.name))
                        else:
                            logging.debug("positional arg found: " + str(token))
                            positional.append(token)
                    else:
                        logging.debug("convert main protoargs field name into long arg name: " + str(token))
                        code += t \
                                .replace("%FUNCTION%", self.__convertToGoType(token).capitalize() + "Var") \
                                .replace("%OPTIONS%", self.__convertToArgName(token.name) ) \
                                .replace("%DESCRIPTION%",token.description) \
                                .replace("%PTYPE%", token.type) \
                                .replace("%ARGNAME%", token.name) \
                                .replace("%FREQUENCY%", token.field.upper()) \
                                .replace("%DEFAULT%", \
                                ("\"" + token.value + "\"" if token.type == pt_string else "false" if len(token.value) == 0 and token.type == pt_bool else "0" if len(token.value) == 0 else token.value) ) \
                                .replace("%TYPE%", \
                                (", type=" + self.__convertToGoType(token) if token.type != pt_bool else "") ) \
                                .replace("%REQUIRED%", \
                                ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                .replace("%REPEATED%", \
                                ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                .replace("%WITHVALUE%", \
                                ("true" if token.type != pt_bool or token.field == paTokenizer.pf_repeated else "false") ) \
                                .replace("%VARIABLE%", "config." + self.__convertToBashName(token.name))

                        #if len(token.name) == 1:
                        #    code += "\n                   .short('" + self.__convertToArgName(token.name) + "')" # convert into args
                        #else:
                        #    code += "\n                   .long(r#\"" + self.__convertToArgName(token.name) + "\"#)" # convert into args

                        #code += ")\n"
                else:
                    logging.warn("unknown token inside protoargs structure: " + str(token))

        return code

    def __flagProgramUsage(self, tokens):
        template = r"""
  %OPTIONS%%NEWLINE%%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:%DEFAULT%})"""
        templateRequired = r"""
  %OPTIONS%%NEWLINE%%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%})"""
        templateRepeated = r"""
  %OPTIONS%%NEWLINE%%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%})"""

        shiftDetailed = 0

        shift = 25 # number of spaces to shift for detailed description
        shiftSpace = ""
        for x in range(0,shift):
            shiftSpace += " "

        shortOptional = "" # short usage for optional arguments
        shortRequired = "" # short usage required arguments
        shortPositional = "" # short usage positional arguments
        optional = "" # optional detailed description
        required = "" # required detailed description
        positional = "" # positional detailed description

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
                    elif token.field == paTokenizer.pf_repeated:
                        t = templateRepeated

                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) > 0:
                            # add all links as options
                            logging.debug("links found for: " + str(token) + "\n" + str(links))
                            options = ""
                            argument = ""
                            for link in links:
                                if len(options) > 0:
                                    options += ", "
                                    argument += "|"
                                #options += self.__convertToArgName(link.name) # convert into args
                                if len(link.name) == 1:
                                    options += "-" + self.__convertToArgName(link.name)
                                    argument += "-" + self.__convertToArgName(link.name)
                                else:
                                    options += "--" + self.__convertToArgName(link.name)
                                    argument += "--" + self.__convertToArgName(link.name)

                            if token.type != pt_bool:
                                options += " " + token.name

                            if options:
                                spaces = shift - (1 + len(options)) # calculate needed spaces
                                for x in range(1,spaces):
                                    options += " "
                                updated = t \
                                        .replace("%OPTIONS%", options) \
                                        .replace("%NEWLINE%", "\n" + shiftSpace if spaces < 3 else "") \
                                        .replace("%DESCRIPTION%",token.description) \
                                        .replace("%PTYPE%", token.type) \
                                        .replace("%ARGNAME%", token.name) \
                                        .replace("%FREQUENCY%", token.field.upper()) \
                                        .replace("%DEFAULT%", \
                                        ("\"" + token.value + "\"" if token.type == pt_string else "false" if len(token.value) == 0 and token.type == pt_bool else "0" if len(token.value) == 0 else token.value) ) \
                                        .replace("%TYPE%", \
                                        (", type=" + self.__convertToGoType(token) if token.type != pt_bool else "") ) \
                                        .replace("%REQUIRED%", \
                                        ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                        .replace("%REPEATED%", \
                                        ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                        .replace("%WITHVALUE%", \
                                        ("true" if token.type != pt_bool else "false") ) \
                                        .replace("%VARIABLE%", "config." + token.name)


                                if token.field == paTokenizer.pf_required:
                                    if len(shortRequired) > 0:
                                        shortRequired += " "
                                    shortRequired += argument
                                    if token.type != pt_bool:
                                        shortRequired += " " + token.name
                                    required += updated
                                elif token.field == paTokenizer.pf_repeated:
                                    if len(shortOptional) > 0:
                                        shortOptional += " "
                                    shortOptional += "[" + argument
                                    if token.type != pt_bool:
                                        shortOptional += " " + token.name + " [" + argument + " " + token.name + " ...]" + "]"
                                    else:
                                        shortOptional += " [" + argument + " ...]" + "]"
                                    optional += updated
                                else:
                                    if len(shortOptional) > 0:
                                        shortOptional += " "
                                    shortOptional += "[" + argument
                                    if token.type != pt_bool:
                                        shortOptional += " " + token.name + "]"
                                    else:
                                        shortOptional += "]"
                                    optional += updated
                        else:
                            options = token.name
                            spaces = shift - (1 + len(options)) # calculate needed spaces
                            for x in range(1,spaces):
                                options += " "
                            updated = templateRequired \
                                    .replace("%OPTIONS%", options) \
                                    .replace("%NEWLINE%", "\n" + shiftSpace if spaces < 3 else "") \
                                    .replace("%DESCRIPTION%",token.description) \
                                    .replace("%PTYPE%", token.type) \
                                    .replace("%ARGNAME%", token.name) \
                                    .replace("%FREQUENCY%", paTokenizer.pf_required.upper()) \
                                    .replace("%DEFAULT%", \
                                    ("\"" + token.value + "\"" if token.type == pt_string else token.value) ) \
                                    .replace("%TYPE%", \
                                    (", type=" + self.__convertToGoType(token) if token.type != pt_bool else "") ) \
                                    .replace("%REQUIRED%", \
                                    ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                    .replace("%REPEATED%", \
                                    ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                    .replace("%WITHVALUE%", \
                                    ("true" if token.type != pt_bool else "false") ) \
                                    .replace("%VARIABLE%", "config." + token.name)

                            logging.debug("positional arg found: " + str(token))
                            if len(shortPositional) > 0:
                                shortPositional += " "
                            shortPositional += token.name
                            if token.field == paTokenizer.pf_repeated:
                                shortPositional += " [" + token.name + " ...]"
                            positional += updated
                    else:
                        logging.debug("convert main protoargs field name into long arg name: " + str(token))
                        if len(token.name) == 1:
                            argument = "-" + self.__convertToArgName(token.name)
                        else:
                            argument = "--" + self.__convertToArgName(token.name)
                        options = argument
                        if token.type != pt_bool:
                            options += " value"
                        spaces = shift - (1 + len(options)) # calculate needed spaces
                        for x in range(1,spaces):
                            options += " "
                        updated = t \
                                .replace("%FUNCTION%", self.__convertToGoType(token).capitalize() + "Var") \
                                .replace("%OPTIONS%", options) \
                                .replace("%NEWLINE%", "\n" + shiftSpace if spaces < 3 else "") \
                                .replace("%DESCRIPTION%",token.description) \
                                .replace("%PTYPE%", token.type) \
                                .replace("%ARGNAME%", token.name) \
                                .replace("%FREQUENCY%", token.field.upper()) \
                                .replace("%DEFAULT%", \
                                ("\"" + token.value + "\"" if token.type == pt_string else "false" if len(token.value) == 0 and token.type == pt_bool else "0" if len(token.value) == 0 else token.value) ) \
                                .replace("%TYPE%", \
                                (", type=" + self.__convertToGoType(token) if token.type != pt_bool else "") ) \
                                .replace("%REQUIRED%", \
                                ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                .replace("%REPEATED%", \
                                ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                .replace("%WITHVALUE%", \
                                ("true" if token.type != pt_bool or token.field == paTokenizer.pf_repeated else "false") ) \
                                .replace("%VARIABLE%", "config." + token.name)

                        if token.field == paTokenizer.pf_required:
                            if len(shortRequired) > 0:
                                shortRequired += " "
                            shortRequired += argument
                            if token.type != pt_bool:
                                shortRequired += " value"
                            required += updated
                        elif token.field == paTokenizer.pf_repeated:
                            if len(shortOptional) > 0:
                                shortOptional += " "
                            shortOptional += "[" + argument
                            if token.type != pt_bool:
                                shortOptional += " value [" + argument + " value ...]" + "]"
                            else:
                                shortOptional += " [" + argument + " ...]" + "]"
                            optional += updated
                        else:
                            if len(shortOptional) > 0:
                                shortOptional += " "
                            shortOptional += "[" + argument
                            if token.type != pt_bool:
                                shortOptional += " value]"
                            else:
                                shortOptional += "]"
                            optional += updated

                else:
                    logging.warn("unknown token inside protoargs structure: " + str(token))

        # generate final usage code
        code = r"""    block = "\nusage: ${program} """
        if len(shortRequired):
            code += " " + shortRequired
        if len(shortOptional):
            code += " " + shortOptional
        if len(shortPositional):
            code += " " + shortPositional
        code += "\""
        code += r"""
    usage = splitShortUsage "${block}" "${limit}"
"""

        code += r"""
    usage += "\n\n"
    usage += "${description}"
"""

# TODO
#        if len(required) > 0:
#            code += r"""    usage += "\n\nrequired arguments:""" + "\"\n"
#            code += "    block = \"" + required + "\"\n"
#            code += r"""    usage += splitUsage(block, limit)""" + "\n"
#
#        if len(positional) > 0:
#            code += r"""    usage += "\n\nrequired positional arguments:""" + "\"\n"
#            code += "    block = \"" + positional + "\"\n"
#            code += r"""    usage += splitUsage(block, limit)""" + "\n"
#
#        if len(optional) > 0:
#            #code += r"""    usage += "\n\n" + `optional arguments:`""" + "\n"
#            #code += r"""    usage += `""" + optional + r"""`""" + "\n"
#
#            code += r"""    usage += "\n\n" + `optional arguments:`""" + "\n"
#            code += r"""    block = `""" + optional + r"""`""" + "\n"
#            code += r"""    usage += splitUsage(block, limit)""" + "\n"

        code += r"""    usage += "\n" """
        return code

