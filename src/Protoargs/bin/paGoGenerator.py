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

# go types
go_float = "float32"
go_double = "float64"
go_int32 = "int32"
go_uint32 = "uint32"
go_int64 = "int64"
go_uint64 = "uint64"
go_bool = "bool"
go_string = "string"

# END GLOBALS ###################################3

class Generator:

    __path = "" # path to proto file
    __goCommonPath = "" # path to common source file
    __goPath = "" # path to source file
    __mod = "" # go package name
    __go = "" # source file content

    def __init__(self, path, dst):
        self.__path = path
        filename = os.path.splitext( os.path.basename(path) )[0]
        base = os.path.join(dst, filename)
        self.__goCommonPath = os.path.join(dst, "protoargs.go")
        self.__goPath = base + "_pa.go"
        self.__mod = filename + "_pa"

    def getSourceFileData(self):
        return self.__go

    def getSourceFilePath(self):
        return self.__goPath

    def getCommonFilePath(self):
        return self.__goCommonPath

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
                self.__go = self.__generateSourceFromTokens(tokens) + self.__generateCommonSource()

                # save code to files
                self.__saveFileData( self.getSourceFilePath(), self.__go )

        return data

    # convert protobuf config names into go code names
    def __convertToGoName(self, name):
        return "Arg" + name

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
            pyType = go_int32
        if protoType == pt_uint32:
            pyType = go_uint32
        if protoType == pt_int64:
            pyType = go_int64
        if protoType == pt_uint64:
            pyType = go_uint64
        if protoType == pt_bool:
            pyType = go_bool
        if protoType == pt_string:
            pyType = go_string
        if protoType == pt_float:
            pyType = go_float
        if protoType == pt_double:
            pyType = go_double

        return pyType

    def __convertToDefaultValue(self, token):
        if not token.value:
            return ""
        return (r'r"""' + token.value + r'"""' if token.type == pt_string else token.value).replace("true", "True").replace("false", "False")

    # generate common interfaces source code
    def __generateCommonSource(self):
#        code = """package protoargs
#
#import (
#    "strconv"
#    "fmt"
#)
#
#"""
        code = r"""
/// If flag was found among provided arguments
///
/// # Arguments
///
/// * `flags` - flag specific FlagSet, see PrepareOptions for details
/// * `name` - name of flag to search
///
/// returns true if flag was present among provided arguments
func isFlagPassed(flags *flag.FlagSet, name string) bool {
    found := false
    flags.Visit(func(f *flag.Flag) {
        if f.Name == name {
            found = true
        }
    })
    return found
}

/***************************************************************************\
// Option types
\***************************************************************************/

"""

        types = [go_string, go_bool, go_int32, go_uint32, go_int64, go_uint64, go_float, go_double]
        for gotype in types:
            code += r"""
type (
    %Type%Value struct { // A %type% value for %Type%Option interface.
        val %type% // possible default value
        present bool // is true - flag showing argument was present in command line
    }
)

func (option %Type%Value) Get() %type% { return option.val }
func (option %Type%Value) IsSet() bool { return option.present }
func (option *%Type%Value) SetPresent(present bool) { option.present = present }

func (i *%Type%Value) String() string {
    return fmt.Sprint( %type%(i.Get()) )
}

func (i *%Type%Value) Set(value string) error {
    var err error = nil
    %CONVERTER%
    *i = %Type%Value{%type%(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type Array%Type%Flags []%type%

func (a *Array%Type%Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *Array%Type%Flags) Set(value string) error {
    var err error = nil
    %CONVERTER%
    *i = append(*i, %type%(typedValue))
    return err
}
""" \
        .replace("%Type%", gotype.capitalize()) \
        .replace("%type%", gotype) \
        .replace("%CONVERTER%", \
            (r"""typedValue, err := strconv.ParseBool(value)""" if gotype == go_bool \
            else r"""typedValue, err := strconv.ParseInt(value, 10, 32)""" if gotype == go_int32 \
            else r"""typedValue, err := strconv.ParseInt(value, 10, 64)""" if gotype == go_int64 \
            else r"""typedValue, err := strconv.ParseUint(value, 10, 32)""" if gotype == go_uint32 \
            else r"""typedValue, err := strconv.ParseUint(value, 10, 64)""" if gotype == go_uint64 \
            else r"""typedValue, err := strconv.ParseFloat(value, 32)""" if gotype == go_float \
            else r"""typedValue, err := strconv.ParseFloat(value, 64)""" if gotype == go_double \
            else r"""typedValue := value"""))

        return code

    # generate go source file content
    def __generateSourceFromTokens(self, tokens):
        head = "package " + self.__mod
        head += """

import (
    "os"
    "flag"
    "fmt"
    "errors"
    "strconv"
    "regexp"
    "strings"
)

"""

        tail = ""
        body = ""

        # add configuration structure to store typed values
        body += """
/// Configuration structure to hold all parsed arguments as string typed entities
type Config struct {
"""
        # register fields
        body += self.__flagStructureFields(tokens)

        body += """
}
"""

        # add prepare_options function binding
        body += """
/// Options preparation
///
/// # Arguments
///
/// * `program` - Program name to display in help message
///
/// returns FlagSet instance ready to do parsing and configuration structure which memory is used
func PrepareOptions(program string) (*flag.FlagSet, *Config) {
    flags := flag.NewFlagSet(program, flag.ContinueOnError)
"""
        # initialize default config memory
        body += self.__flagInitConfig(tokens)

        # register arguments
        body += self.__flagProgramOptions(tokens)

        body += """

    return flags, config
}
"""


        # add usage function binding
        body += """
/// Get usage string
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `description` - Description to display in help message
///
/// returns String with usage information
func Usage(program string, description string) string {
"""
        # register usage arguments
        body += self.__flagProgramUsage(tokens)

        body += r"""

    return usage
}

"""

        # add parsing functions
        body += """
/// Parse command line arguments, and return filled configuration
/// Simple and straight forward, thus recommended
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `description` - Description to display in help message
///
/// returns Result with configuration structure, or error message
func Parse(program string, description string, allow_incomplete bool) (*Config, error) {
    return ParseExt(program, os.Args, description, allow_incomplete)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments as string slice
/// * `description` - Description to display in help message
/// * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
/// wrong type cast will produce error anyway
///
/// returns Result with configuration structure, or error message
func ParseExt(program string, args []string, description string, allow_incomplete bool) (*Config, error) {
    flags, config := PrepareOptions(program)

    usage := Usage(program, description)
    flags.Usage = func() {
        fmt.Printf("%s", usage)
    }

    err := flags.Parse(args[1:])
    if err != nil {
        return config, err
    }

"""

        # register fields
        body += self.__flagStructureFill(tokens)

        body += r"""
    return config, nil
}


/***************************************************************************\
// Internal functions
\***************************************************************************/

/// Split short usage into shifted lines with specified line limit
///
/// # Arguments
///
/// * `usage` - string of any length to split
/// * `limit` - size of line, which should not be violated
///
/// returns Properly formatted short usage string
func splitShortUsage(usage string, limit uint32) string {
    var restokens []string

    rule := regexp.MustCompile(`\ \[`) // trying to preserve [.*] options on the same line
    subrule := regexp.MustCompile(`\]\ `) // split on last ]
    spacerule := regexp.MustCompile(`\ `) // split with space for the rest

    tokens := rule.Split(usage, -1)
    for index, token := range tokens {
        if index > 0 {
            token = `[` + token
        }
        subtokens := subrule.Split(token, -1)
        if len(subtokens) > 1 {
            for subindex, subtoken := range subtokens {
                if subindex != (len(subtokens)-1) {
                    subtoken += `]`
                }
                subsubtokens := spacerule.Split(subtoken, -1)
                if len(subsubtokens) > 1 {
                    for _, subsubtoken := range subsubtokens {
                        restokens = append(restokens, subsubtoken)
                    }
                } else {
                    restokens = append(restokens, subtoken)
                }
            }
        } else if token[0] != '[' {
            subtokens := spacerule.Split(token, -1)
            if len(subtokens) > 1 {
                for _, subtoken := range subtokens {
                    restokens = append(restokens, subtoken)
                }
            } else {
                restokens = append(restokens, token)
            }
        } else {
            restokens = append(restokens, token)
        }
    }
    return split(restokens, 25, limit)
}

/// Split usage into shifted lines with specified line limit
///
/// # Arguments
///
/// * `usage` - string of any length to split
/// * `limit` - size of line, which should not be violated
///
/// returns Properly formatted usage string
func splitUsage(usage string, limit uint32) string {
    rule := regexp.MustCompile(`\ `)
    tokens := rule.Split(usage, -1)
    return split(tokens, 25, limit)
}

/// Split usage into shifted lines with specified line limit
///
/// # Arguments
///
/// * `tokens` - set of tokens to which represent words, which better
/// be moved to new line in one piece
/// * `shift` - moved to new line string should start from this position
/// * `limit` - size of line, which should not be violated
///
/// returns Properly formatted usage string
func split(tokens []string, shift uint32, limit uint32) string {
    // calculate shift space
    space := ""
    for i := uint32(0); i < shift; i++ {
        space += " "
    }

    result := ""
    line := ""
    for _, token := range tokens {
        if len(line) > 0 && uint32(len(line) + len(token)) > (limit-1) { // -1 for delimiter
            // push line preserving token as new line
            result += line
            if len(token) > 0 && token[0] != '-' {
                line = "\n" + space + token
            } else {
                line = " " + token
            }
        } else if len(line) > 0 && line[len(line)-1] == '\n' {
            // row finish found
            result += line
            line = " " + token
        } else {
            // append token to line via space
            if len(line) > 0 {
                line += " "
            }
            line += token // strings.TrimRight(token)
        }

        if uint32(len(line)) > limit {
            // split line by limit, the rest is pushed into next line
            var length uint32 = 0
            start := 0
            for i := range line {
                if length == limit {
                    if start > 0 {
                        result += "\n" + space
                    }
                    result += line[start:i]
                    length = 0
                    start = i
                }
                length++
            }
            if strings.TrimRight(line[start:], " ") != "" {
                line = "\n" + space + line[start:]
            } else {
                line = " "
            }
        }
    }
    result += line
    return result
}
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

    def __flagStructureFields(self, tokens):
        template = """    /// %DESCRIPTION%
    %NAME% %TYPE%\n"""
        code = ""

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
                        goType = self.__convertToGoType(token)
                        if token.field == paTokenizer.pf_repeated:
                            goType = "Array" + goType.capitalize() + "Flags"
                        elif token.field == paTokenizer.pf_optional:
                            goType = goType.capitalize() + "Value"
                        elif token.field == paTokenizer.pf_required:
                            goType = goType.capitalize() + "Value"

                        code += template \
                                .replace("%NAME%", self.__convertToGoName(token.name)) \
                                .replace("%TYPE%", goType) \
                                .replace("%DESCRIPTION%", token.description)

        return code

    def __flagStructureFill(self, tokens):
        templateOptional = r""""""


        templateOptionalBool = r"""    config.%NAME%.SetPresent( isFlagPassed(flags, `%ARGUMENT%`) )
"""

        templateRequired = r"""    if !allow_incomplete && !config.%NAME%.IsSet() {
        err%NAME% := errors.New(`Required '%OPTION%' is missing`)
        fmt.Println(err%NAME%)
        fmt.Println(Usage(program, description))
        return config, err%NAME%
    }
"""


        templateRepeated = r""""""

        templatePositional = r"""    if !allow_incomplete && flags.NArg() < %POSITION% {
        err%NAME% := errors.New(`Required positional '%OPTION%' is missing`)
        fmt.Println(err%NAME%)
        fmt.Println(Usage(program, description))
        return config, err%NAME%
    }
    err%NAME% := %VARIABLE%.Set(flags.Arg(%INDEX%))
    if !allow_incomplete && err%NAME% != nil {
        fmt.Println(err%NAME%)
        fmt.Println(Usage(program, description))
        return config, err%NAME%
    }
"""

        templateRepeatedPositional = r"""    if !allow_incomplete && flags.NArg() < %POSITION% {
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
        code = """"""
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
                        goType = self.__convertToGoType(token)

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
                                .replace("%NAME%", self.__convertToGoName(token.name)) \
                                .replace("%ARGUMENT%", argument) \
                                .replace("%OPTION%", self.__convertToArgName(token.name)) \
                                .replace("%TYPE%", goType) \
                                .replace("%VARIABLE%", "config." + self.__convertToGoName(token.name)) \
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
                        goType = self.__convertToGoType(token)
                        if token.field == paTokenizer.pf_repeated:
                            goType = "Array" + goType.capitalize() + "Flags"
                        elif token.field == paTokenizer.pf_optional:
                            goType = goType.capitalize() + "Value"
                        elif token.field == paTokenizer.pf_required:
                            goType = goType.capitalize() + "Value"

                        if token.field != paTokenizer.pf_repeated:
                            code += template \
                                    .replace("%NAME%", self.__convertToGoName(token.name)) \
                                    .replace("%TYPE%", goType) \
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
                                        .replace("%VARIABLE%", "config." + self.__convertToGoName(token.name))
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
                                .replace("%VARIABLE%", "config." + self.__convertToGoName(token.name))

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
        code = r"""
    var limit uint32 = 80
    block := "\n" + `usage: ` + program + `"""
        if len(shortRequired):
            code += " " + shortRequired
        if len(shortOptional):
            code += " " + shortOptional
        if len(shortPositional):
            code += " " + shortPositional
        code += "`"
        code += r"""
    usage := splitShortUsage(block, limit)
"""

        code += r"""
    usage += "\n\n"
    usage += description
"""

        if len(required) > 0:
            code += r"""    usage += "\n\n" + `required arguments:`""" + "\n"
            code += r"""    block = `""" + required + r"""`""" + "\n"
            code += r"""    usage += splitUsage(block, limit)""" + "\n"

        if len(positional) > 0:
            code += r"""    usage += "\n\n" + `required positional arguments:`""" + "\n"
            code += r"""    block = `""" + positional + r"""`""" + "\n"
            code += r"""    usage += splitUsage(block, limit)""" + "\n"

        if len(optional) > 0:
            #code += r"""    usage += "\n\n" + `optional arguments:`""" + "\n"
            #code += r"""    usage += `""" + optional + r"""`""" + "\n"

            code += r"""    usage += "\n\n" + `optional arguments:`""" + "\n"
            code += r"""    block = `""" + optional + r"""`""" + "\n"
            code += r"""    usage += splitUsage(block, limit)""" + "\n"

        code += r"""    usage += "\n" """
        return code

