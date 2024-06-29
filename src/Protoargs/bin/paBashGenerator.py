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
    def __convertToBashType(self, token):
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
    %PACKAGE%_PROTOARGS_USAGE=""
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

    %PACKAGE%_PROTOARGS_USAGE="$(cat << PROTOARGS_EOM
"""

        body += self.__parasiteUsage(self.__path)

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

########################################################################
# Helpers
########################################################################

# Keep some number of first arguments, remove the rest
#
# Arguments:
#
# * `keep` - Number of arguments to keep
# * `args` - Command line arguments, list, use $@ to pass them
#
# returns `%PACKAGE%_PROTOARGS_ARGS` Resulting set of args
function %PACKAGE%_remove_args_tail() #(keep, args)
{
    %PACKAGE%_PROTOARGS_ARGS=()
    local keep=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$keep" ]]; do
        %PACKAGE%_PROTOARGS_ARGS+=("$1")
        shift
        pos=$((pos + 1))
    done
}

# Remove some number of first arguments, keep the rest
#
# Arguments:
#
# * `erase` - Number of arguments to remove
# * `args` - Command line arguments, list, use $@ to pass them
#
# returns `%PACKAGE%_PROTOARGS_ARGS` Resulting set of args
function %PACKAGE%_keep_args_tail()
{
    local erase=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$erase" ]]; do
        shift
        pos=$((pos + 1))
    done
    %PACKAGE%_PROTOARGS_ARGS=("$@")
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
                        echo "${%PACKAGE%_PROTOARGS_USAGE}"
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
                        echo "${%PACKAGE%_PROTOARGS_USAGE}"
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
                        echo "${%PACKAGE%_PROTOARGS_USAGE}"
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
                        echo "${%PACKAGE%_PROTOARGS_USAGE}"
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
                        bashType = self.__convertToBashType(token)

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
                                    template = templateDefaultRepeated
                                    template_eq = templateDefaultRepeatedEquals
                            elif token.type == pt_string:
                                template = templateString
                                template_eq = templateStringEquals
                                if token.field == paTokenizer.pf_repeated:
                                    template = templateDefaultRepeated
                                    template_eq = templateDefaultRepeatedEquals
                            else:
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
                                    else r"""! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]"""  if token.type == pt_int32 or token.type == pt_int64 \
                                    else r"""! [[ "${value}" =~ ^[0-9]+$ ]]"""  if token.type == pt_uint32 or token.type == pt_uint64 \
                                    else r"""[ -z "0" ]""" \
                                    )) \

        code += """
            -*|--*)
                if ! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]] || ! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
                    echo "[ERR] Unknown option '$1'"
                    echo "${%PACKAGE%_PROTOARGS_USAGE}"
                    return 1
                fi
                POSITIONAL_ARGS+=("$1") # save positional numeric arg
                shift # past argument
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
        echo "[ERR] Positional '%TRUENAME%' parameter is not set"
        echo "${%PACKAGE%_PROTOARGS_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[%POSITION%]}"
    if %CHECKER%; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional '%TRUENAME%' parameter expected to be of type '%TYPE%' but value is '$value'"
            echo "${%PACKAGE%_PROTOARGS_USAGE}"
            return 1
        fi
    else
        %NAME%="${POSITIONAL_ARGS[%POSITION%]}"
        %NAME%_PRESENT=true
    fi
"""

        templatePositionalRepeated = r"""
    if [ "$allow_incomplete" == false ] && [ %POSITION% -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "[ERR] Positional '%TRUENAME%' parameter is not set, needs to be at least 1"
        echo "${%PACKAGE%_PROTOARGS_USAGE}"
        return 1
    fi
    local expected=$((${#POSITIONAL_ARGS[@]} - %POSITION%))
    local position=%POSITION%
    local processed=0
    while [[ "$%NAME%_COUNT" -lt "$expected" ]] && [[ "$processed" -lt "$expected" ]]; do
        local value="${POSITIONAL_ARGS[$position]}"
        if %CHECKER%; then
            if [ "$allow_incomplete" == false ]; then
                echo "[ERR] Positional '%TRUENAME%' parameter expected to be of type '%TYPE%' but value is '$value'"
                echo "${%PACKAGE%_PROTOARGS_USAGE}"
                return 1
            fi
        else
            %NAME%+=("${POSITIONAL_ARGS[$position]}")
            %NAME%_COUNT=$(($%NAME%_COUNT + 1))
        fi
        position=$((position + 1))
        processed=$((processed + 1))
    done
    if [ "$%NAME%_COUNT" -gt 0 ]; then
        %NAME%_PRESENT=true
    fi

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
                        bashType = self.__convertToBashType(token)

                        if positional:
                            logging.debug("Fill positional name: " + str(token))
                            template = templatePositionalDefault
                            if token.field == paTokenizer.pf_repeated:
                                template = templatePositionalRepeated
                            code += template \
                                    .replace("%NAME%", self.__convertToBashName(token.name)) \
                                    .replace("%TYPE%", bashType) \
                                    .replace("%TRUENAME%", token.name) \
                                    .replace("%POSITION%", str(position-1)) \
                                    .replace("%ARGUMENT%", argument) \

                            # checker
                            code = code.replace("%CHECKER%", ( \
                                    r"""[ "${value}" != true ] && [ "${value}" != false ]""" if token.type == pt_bool \
                                    else r"""! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]]"""  if token.type == pt_double or token.type == pt_float \
                                    else r"""! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]"""  if token.type == pt_int32 or token.type == pt_int64 \
                                    else r"""! [[ "${value}" =~ ^[0-9]+$ ]]"""  if token.type == pt_uint32 or token.type == pt_uint64 \
                                    else r"""[ -z "0" ]""" \
                                    )) \

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
        echo "${%PACKAGE%_PROTOARGS_USAGE}"
        return 1
    fi
"""

        templateRepeated = r""""""

        templatePositional = r""""""

        templateRepeatedPositional = r""""""
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
                        bashType = self.__convertToBashType(token)

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

