#!/usr/bin/python

import os
import sys
import configparser

class Configuration:

    __config = configparser.SafeConfigParser()

    __mainSection = "main"
    __valueOutput = "outputpath"
    __valueInput = "inputfile"

    def __init__(self):
        self.__config.add_section( self.__mainSection )

    def printConfiguration(self):
        # List all contents
        print("List all contents")
        config = self.__config
        for section in config.sections():
            print(("Section: %s" % section))
            for options in config.options(section):
                print(("\t- %s:::%s:::%s" % (options,
                                          config.get(section, options),
                                          str(type(options)))))

    def setOutputPath(self, path):
        self.__config.set(self.__mainSection, self.__valueOutput, path)

    def getOutputPath(self):
        return self.__config.get(self.__mainSection, self.__valueOutput)

    def setProtoPath(self, path):
        self.__config.set(self.__mainSection, self.__valueInput, path)

    def getProtoPath(self):
        return self.__config.get(self.__mainSection, self.__valueInput)


class ArgsParser:

    config = Configuration()

    def usage(self):

        usage = """python protoargs.py -o <out DIR> -i PROTOFILE
            out DIR         [mandatory] path to output directory
            PROTOFILE       [mandatory] path to proto file
            """
        return usage

    def parse(self, argv):
        import getopt

        dst = ""
        proto = ""

        try:
            opts, args = getopt.getopt(argv,"o:i:")
        except getopt.GetoptError:
            print(self.usage())
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print(self.usage())
                sys.exit()
            elif opt in ("-o"):
                dst = arg
                self.config.setOutputPath(arg)
            elif opt in ("-i"):
                proto = arg
                self.config.setProtoPath(arg)
            else:
                print("[ERR] Unknown argument" + arg)

        if not dst or not proto:
            print("[INF] destination is " + dst)
            print("[INF] proto file path is " + proto)
            print("[ERR] destination is empty or no proto file specified")
            print(self.usage())
            sys.exit(1)

        print(self.config.printConfiguration())

# GLOBAL DEFS ###################################3

#class Protoargs:
pa_main = "protoargs"
pa_links = "protoargs_links"

#class ProtoDirectives:
pd_package = "package"
pd_message = "message"
pd_enum = "enum"
pd_field = "field"
pd_end = "}"

#class ProtoFields:
pf_required = "required"
pf_optional = "optional"
pf_repeated = "repeated"

#class ProtoTypes:
pt_int32 = "int32"
pt_uint32 = "uint32"
pt_int64 = "int64"
pt_uint64 = "uint64"
pt_bool = "bool"
pt_string = "string"

# c++ types
cc_int32 = "int32_t"
cc_uint32 = "uint32_t"
cc_int64 = "int64_t"
cc_uint64 = "uint64_t"
cc_bool = "bool"
cc_string = "std::string"

# END GLOBALS ###################################3

class ProtoToken:
    directive = ""
    field = ""
    type = ""
    name= ""
    position = ""
    value = ""
    description = ""

    def valid(self):
        return bool(self.directive)

    def __repr__(self):
        return "(" + self.directive + "," + self.field + "," + self.type + "," + self.name + "," + self.position + "," + self.value + ",'" + self.description + "')"

class ProtoTokenizer:

    __tokens = [] # result of lines parsing

    def getTokens(self):
        return self.__tokens

    # Exclude directive instances
    def excludeDirective(self, directive, name):
        if directive == pd_message or directive == pd_enum: # no other directive possible
            tokens = self.__tokens
            filteredTokens = []
            skip = False;
            for token in tokens:
                if not skip:
                    #print "[TST] " + str(token) + " Check: " + directive + ", " + name
                    if directive == token.directive and name == token.name:
                        skip = True # skipping, starting from current line
                    #elif directive != token.directive:
                    else:
                        filteredTokens.append(token) # let the token stay
                elif token.directive == pd_end:
                    skip = False
            self.__tokens = filteredTokens
        return self

    # Exclude unused structures from tokens
    def excludeUnused(self):
        tokens = self.__tokens
        unusedTokens = []
        for token in tokens:
            if token.directive == pd_enum:
                print("[WRN] enums are not supported, exclude " + token.name)
                unusedTokens.apend(token)
            elif token.directive == pd_message:
                if token.name.find(pa_main) == -1 and token.name.find(pa_links) == -1: # Check for predefined messages
                    print("[WRN] messages are not needed, exclude " + token.name)
                    unusedTokens.append(token)

        # removing structures
        for unused in unusedTokens:
            self.excludeDirective(unused.directive, unused.name)

        return self

    def getToken(self, directive, name):
        found = False
        tokens = self.__tokens
        result = ProtoToken()
        for token in tokens:
            if token.directive == directive and token.name == name:
                result = token
                break
        return result

    def check(self): # Add more checks
        print("-----------------------------------------------------")
        # check if needed messages present
        foundProtoargs = self.getToken(pd_message, pa_main).valid()
        foundProtoargsLinks = self.getToken(pd_message, pa_links).valid()

        print("[INF] " + pa_main + " message: " + str(foundProtoargs));
        print("[INF] " + pa_links +" message: " + str(foundProtoargsLinks));
        print("-----------------------------------------------------")

        return foundProtoargs

    # parse field line and return token for it
    def createFieldToken(self, line):
        line = line.replace("\t"," ");
        chunks = line.split(" ")

        token = ProtoToken()
        token.directive = pd_field
        token.field = chunks[0].strip()
        token.type = chunks[1].strip()
        token.name = chunks[2].strip()
        token.position = chunks[4].replace(";","").strip()

        # discover default value
        nocomment = self.__removeComment(line)
        if nocomment.find("]") != -1:
            token.value = nocomment \
                    .split("]")[0] \
                    .split("[")[1] \
                    .split("=")[1] \
                    .strip()
            if token.value[0] == '"': # remove " from string
                token.value = token.value[1:len(token.value)-1]

        # comment on the same line is our description
        token.description = line.split(";")[1].strip()
        token.description = token.description[2:len(token.description)].strip() # remove starting //

        return token

    def createPackageToken(self, line):
        line = self.__removeComment(line)
        token = ProtoToken()
        token.directive = pd_package
        token.name = line \
                .replace(";","") \
                .replace(pd_package,"") \
                .strip()
        return token

    def __createMessageToken(self, line):
        line = self.__removeComment(line)
        token = ProtoToken()
        token.directive = pd_message
        token.name = line \
                .replace(";","") \
                .replace(pd_message,"") \
                .strip()
        return token

    def __createEndToken(self, line):
        token = ProtoToken()
        token.directive = pd_end
        return token

    def __removeComment(self, line):
        if line.find(";") == -1:
            return self.__isEntireLineComment(line)
        else:
            return line.split(";")[0] + ";"

    # remove what we think is a comment, and check if this entire line comment
    def __isEntireLineComment(self, line):
        fieldChunks = line.split("//")
        return fieldChunks[0].strip()

    def tokenize(self, data):
        # tokenizing line by line
        for line in data:
            sline = line.strip() # make striped line
            # remove what we think is a comment, and check if this entire line comment
            # Note: we still need comments for fields, it is out field description
            if self.__isEntireLineComment(sline):
                if sline.find(pf_required) != -1 or \
                   sline.find(pf_optional) != -1 or \
                   sline.find(pf_repeated) != -1:
                    print("[DBG] " + sline)
                    token = self.createFieldToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_package) != -1:
                    print("[DBG] " + sline)
                    token = self.createPackageToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_message) != -1:
                    print("[DBG] " + sline)
                    token = self.__createMessageToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_end) != -1:
                    print("[DBG] " + sline)
                    token = self.__createEndToken(sline)
                    self.__tokens.append(token)

        return self


class CppGenerator:

    __path = "" # path to proto file
    __pbhPath = ""  # path to protobuf header file
    __pbhName = ""  # name of protobuf header file for include
    __ccPath = "" # path to source file
    __hPath = ""  # path to header file
    __cc = "" # source file content
    __h = ""  # header content

    def __init__(self, path):
        self.__path = path
        base = os.path.splitext(path)[0]
        self.__hPath = base + ".pa.h"
        self.__ccPath = base + ".pa.cc"
        self.__pbhPath = base + ".pb.h"
        head, tail = os.path.split(self.__pbhPath)
        self.__pbhName = tail

    def getSourceFileData(self):
        return self.__cc

    def getHeaderFileData(self):
        return self.__h

    def getSourceFilePath(self):
        return self.__ccPath

    def getHeaderFilePath(self):
        return self.__hPath

    # load file entirely
    def loadFileData(self, path):
        try:
            with open(path, "r") as index:
                lines = index.readlines()
                index.close()
                return lines
        except:
            print("[ERR] Could not read file because of error")
            return ""

    def __saveFileData(self, path, data):
        try:
            with open(path, "w") as index:
                index.write(data)
                index.close()
                return True;
        except:
            print("[ERR] Could not write to file \"" + path + "\" because of error")
            return False;

    # parse proto file and generate c++ files
    def generate(self):
        #load proto file
        data = self.loadFileData(path)
        result = len(data) != 0
        if result:
            # tokenize proto file data
            tokenizer = ProtoTokenizer() \
                    .tokenize(data) \
                    .excludeUnused() \

            result = tokenizer.check() # check tokens
            if result:
                tokens = tokenizer.getTokens()

                # DBG
                for token in tokens:
                    print("[DBG] " + str(token))

                # generate souce code
                self.__h = self.__generateHeaderFromTokens(tokens)
                self.__cc = self.__generateSourceFromTokens(tokens)

                # save code to files
                self.__saveFileData( self.getHeaderFilePath(), self.__h )
                self.__saveFileData( self.getSourceFilePath(), self.__cc )

        return data

    # convert protobuf config names into c code names
    def __convertToCCName(self, name):
        return name.lower()

    # convert protobuf config names into args
    def __convertToArgName(self, name):
        return name.replace("_","-")

    # convert protobuf config types into c++ types
    def __convertToCCType(self, token):
        ccType = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            ccType = cc_int32
        if protoType == pt_uint32:
            ccType = cc_uint32
        if protoType == pt_int64:
            ccType = cc_int64
        if protoType == pt_uint64:
            ccType = cc_uint64
        if protoType == pt_bool:
            ccType = cc_bool
        if protoType == pt_string:
            ccType = cc_string

        # value may be repeated
        if token.field == pf_repeated:
            ccType = "std::vector<" + ccType + ">"

        return ccType

    def __converterFromString(self, token):
        stringConverter = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            stringConverter = "stoi"
        if protoType == pt_uint32:
            stringConverter = "stoi"
        if protoType == pt_int64:
            stringConverter = "stoll"
        if protoType == pt_uint64:
            stringConverter = "stoll"
        if protoType == pt_bool:
            stringConverter = "0 != stoi"
        if protoType == pt_string:
            stringConverter = ""

        return stringConverter


    # generate c++ header file content
    def __generateHeaderFromTokens(self, tokens):

        head = """#pragma once

"""
        head += "#include <string>\n"
        head += "#include <set>\n"
        head += "#include <regex>\n"
        head += "#include <cxxopts.hpp>\n" # register cxxopts header
        head += "#include \"" + self.__pbhName + "\"\n\n"

        tail = ""
        body = ""
        for token in tokens:
            if token.directive == pd_package:
                print("[DBG] " + str(token))
                namespaces = token.name.split(".") #discover namespaces
                for namespace in namespaces:
                    ns = namespace.strip()
                    body += "namespace " + ns + " {\n"
                    tail = "}//namespace " + ns + "\n" + tail

        body += """
    class ProtoArgs
    {
        public:
            ProtoArgs() {}
            virtual ~ProtoArgs() {}

            /**
             * @brief Get program usage
             * @param program Program name for usage description
             * @return Usage string
             */
            virtual std::string usage(const std::string& program) const;

            /**
             * @brief Parse arguments and get object with configuration
             * @param program Program name for usage description
             * @param argc    Command line args num
             * @param argv[]  Command line args
             * @param allowIncomplete  Fills valid configuration fields with no errors, ignoring requires
             * @return Configuration or nullptr if failed
             */
            virtual protoargs* parse(const std::string& program, int argc, char* argv[], bool allowIncomplete = false) const;

            /**
             * @brief In case you want add something, or change
             * e.g. set your own usage output
             * look into cxxopts documentation
             * Note: you should parse it manually from now on
             * @param program Program name for usage description
             * @return Options
             */
            virtual cxxopts::Options prepareOptions(const std::string& program) const;

            /**
             * @brief Filter result, Note: argv will be destroyed on object destruction
             */
            struct ExcludeResult
            {
                ~ExcludeResult() { delete [] argv; }
                int argc;
                char** argv;
            };//struct

            /**
             * @brief Helper function, filter arguments by positions sequence
             * This is useful if you need support multy-commands, like "git add [add args]" and "git commit [commit args]"
             * So at some point you need to remove "add" ot "commit" command argument
             * @param argc Original argc
             * @param argv Original argv
             * @param exclude Array of positions to exclude
             * @return Result with updated argc argv
             */
            virtual ExcludeResult exclude(int argc, char** argv, std::set<int> exclude) const
            {
                char** argvFiltered = new char*[argc];
                int pos = 0;
                int excluded = 0;
                for (int i = 0; i < argc; ++i)
                   if (exclude.find(i+1) == exclude.end())
                      argvFiltered[pos++] = argv[i];
                   else
                      ++excluded;

                ExcludeResult result;
                result.argc = argc - excluded;
                result.argv = argvFiltered;

                return result;
            }
    };//class

"""

        return head + body + tail

    # generate c++ source file content
    def __generateSourceFromTokens(self, tokens):
        head, tail = os.path.split(self.__hPath)
        head = "\n#include \"" + tail + "\"\n\n" # include protoargs header

        tail = ""
        body = ""
        for token in tokens:
            if token.directive == pd_package:
                print("[DBG] " + str(token))
                namespaces = token.name.split(".") #discover namespaces
                for namespace in namespaces:
                    ns = namespace.strip()
                    body += "namespace " + ns + " {\n"
                    tail = "}//namespace " + ns + "\n" + tail

        # add prepareOptions function binding
        body += """
cxxopts::Options ProtoArgs::prepareOptions(const std::string& program) const
{
"""
        # register arguments
        body += self.__cxxoptsProgramDescription(tokens)

        body += self.__cxxoptsProgramOptions(tokens)

        body += """
    return options;
}
"""

        body += """
void updateWithPositionalOptions(cxxopts::Options& options)
{
"""
        # add positional arguments as dummy args, for usage output
        body += self.__cxxoptsPositionalOptions(tokens)

        body += """
}
"""

        # add usage function binding
        body += """
std::string ProtoArgs::usage(const std::string& program) const
{
    auto options = prepareOptions(program);
    updateWithPositionalOptions(options);
    auto usage = options.help();
    usage = std::regex_replace(usage, std::regex("--dummy-"), "        ");
    return usage;
}
"""

        # add prepareOptions function binding
        body += """
protoargs* ProtoArgs::parse(const std::string& program, int argc, char* argv[], bool allowIncomplete /*= false*/) const
{

    auto config = new protoargs();
"""
        # add arguments parsing using cxxopts
        body += self.__cxxoptsParsingBegin(tokens)

        body += self.__cxxoptsRequiredParsing(tokens)
        body += self.__cxxoptsOptionalParsing(tokens)
        body += self.__cxxoptsRepeatedParsing(tokens)
        body += self.__cxxoptsPositionalParsing(tokens)

        body += self.__cxxoptsParsingEnd(tokens)

        body += """
    return config;
}

"""


        return head + body + tail

    # get token by type and name
    def __getToken(self, tokens, directive, name):
        result = ProtoToken()
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
            if token.directive == pd_message and token.name == pa_links:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field and token.value == name: # default link value should be the name of args
                    result.append(token)
        return result


    def __cxxoptsProgramDescription(self, tokens):
        code = """
    cxxopts::Options options(program, "%DESCRIPTION%");
"""
        token = self.__getToken(tokens, pd_message, pa_main)
        if token.valid():
            code = code.replace("%DESCRIPTION%", token.description)

        return code

    def __cxxoptsPositionalOptions(self, tokens):
        template = "(\"%OPTIONS%\", \"%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}\\n\", cxxopts::value<%TYPE%>(), \"--dummy-\")"
        code = """
    options
    .add_options()
"""
        positional = []

        start = False
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:
                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) == 0:
                            positional.append(token)

        # add dummy positional long args, in order to preserve usage output style
        for token in positional:
            print("[DBG] create dummy positional field name as long arg name: " + str(token))
            # add cxxopts option
            prefix = "dummy-"
            code += "       "
            code += template \
                    .replace("%OPTIONS%",prefix + self.__convertToArgName(token.name)) \
                    .replace("%DESCRIPTION%",token.description) \
                    .replace("%PTYPE%", token.type) \
                    .replace("%TYPE%", self.__convertToCCType(token)) \
                    .replace("%ARGNAME%", token.name) \
                    .replace("%FREQUENCY%", pf_required.upper()) \

            code += "\n"

        # end options
        code += "    ;\n\n"

        return code

    def __cxxoptsProgramOptions(self, tokens):
        template = "(\"%OPTIONS%\", \"%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:'%DEFAULT%'}\\n\", cxxopts::value<%TYPE%>(), \"[%ARGNAME%]\")"
        templateRequired = "(\"%OPTIONS%\", \"%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}\\n\", cxxopts::value<%TYPE%>(), \"[%ARGNAME%]\")"
        code = """
    options
    .add_options()
"""
        positional = []

        start = False
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:

                    # set template
                    t = template
                    if token.field == pf_required:
                        t = templateRequired

                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 0:
                            # add all links as options
                            print("[DBG] links found for: " + str(token) + "\n" + str(links))
                            options = ""
                            for link in links:
                                if len(options) > 0 and len(link.name) > 1:
                                    options += ","
                                    options += self.__convertToArgName(link.name) # convert into args
                                elif len(options) > 0 and len(link.name) == 1:
                                    options = self.__convertToArgName(link.name) + "," + options # convert into args
                                else:
                                    options += self.__convertToArgName(link.name) # convert into args

                            # add cxxopts option
                            code += "       "
                            code += t \
                                    .replace("%OPTIONS%",options) \
                                    .replace("%DESCRIPTION%",token.description) \
                                    .replace("%PTYPE%", token.type) \
                                    .replace("%TYPE%", self.__convertToCCType(token)) \
                                    .replace("%ARGNAME%", token.name) \
                                    .replace("%FREQUENCY%", token.field.upper()) \
                                    .replace("%DEFAULT%", token.value)

                            code += "\n"
                        else:
                            print("[DBG] positional arg found: " + str(token))
                            positional.append(token)
                    else:
                        print("[DBG] convert main protoargs field name into long arg name: " + str(token))
                        # add cxxopts option
                        code += "       "
                        code += t \
                                .replace("%OPTIONS%",self.__convertToArgName(token.name)) \
                                .replace("%DESCRIPTION%",token.description) \
                                .replace("%PTYPE%", token.type) \
                                .replace("%TYPE%", self.__convertToCCType(token)) \
                                .replace("%ARGNAME%", token.name) \
                                .replace("%FREQUENCY%", token.field.upper()) \
                                .replace("%DEFAULT%", token.value)
                        code += "\n"
                else:
                    print("[WRN] unknown token inside protoargs structure: " + str(token))

        # do not add positional parsing if no positional args registered
        if len(positional) > 0:
            # add positional values holder
            code += "       "
            code += template \
                    .replace("%OPTIONS%","positional") \
                    .replace("%DESCRIPTION%","This holds all positional values") \
                    .replace("%PTYPE%", "") \
                    .replace("%TYPE%", "std::vector<std::string>") \
                    .replace("%ARGNAME%", "") \
                    .replace("%FREQUENCY%", token.field.upper()) \
                    .replace("%DEFAULT%", "[]")
            code += "\n"

        # end options
        code += "    ;\n\n"

        if len(positional) > 0:
            # add better description for positional values
            posCode = ""
            for pos in positional:
                if posCode:
                    posCode += " "
                if pos.field == pf_repeated:
                    posCode += pos.name + " [" + pos.name + "...]" # psotional repeating, at least one should be present
                else:
                    posCode += pos.name

            code += "    "
            code += "options.positional_help(\"" + posCode + "\");\n"

            # add positional parsing
            code += "    "
            code += "options.parse_positional({\"positional\"});\n"

        return code

    def __cxxoptsParsingBegin(self, tokens):
        code = """
    auto options = prepareOptions(program);
"""
        # add cxxopts parsing
        code += """
    try
    {
        auto result = options.parse(argc, argv);
"""
        return code

    def __cxxoptsParsingEnd(self, tokens):
        code = """
    auto options = prepareOptions(program);
"""
        # add cxxopts parsing
        code += """
    }
    catch (const std::exception& e)
    {
        std::cout << "[ERR] Error parsing option: " << e.what() << std::endl;
        if (!allowIncomplete)
        {
            std::cout << usage(program).c_str() << std::endl;
            delete config;
            return nullptr;
        }//if
    }//catch
"""
        return code

    def __cxxoptsRequiredParsing(self, tokens):
        template = """
        if (result.count("%ARGNAME%") > 0)
        {
            try
            {
                config->set_%SETTER%( result["%ARGNAME%"].as<%TYPE%>() );
            }//try
            catch (const std::exception& e)
            {
                auto value = result["%ARGNAME%"].as<std::string>();
                std::cout << "[ERR] Error parsing option %ARGNAME% with value '" << value << "': " << e.what() << std::endl;
                if (!allowIncomplete)
                {
                    std::cout << usage(program).c_str() << std::endl;
                    delete config;
                    return nullptr;
                }//if
            }//catch
        }
        else if (!allowIncomplete)
        {
            std::cout << "[ERR] REQUIRED '%PNAME%' is not set" << std::endl;
            std::cout << usage(program).c_str() << std::endl;
            delete config;
            return nullptr;
        }//if
"""

        code = ""

        # fill proto object
        start = False
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == pf_required: # this parameter should be present
                            code += template \
                                    .replace("%ARGNAME%", link) \
                                    .replace("%PNAME%", token.name) \
                                    .replace("%TYPE%", self.__convertToCCType(token)) \
                                    .replace("%SETTER%", self.__convertToCCName(token.name))

        return code

    def __cxxoptsOptionalParsing(self, tokens):
        template = """
        if (result.count("%ARGNAME%"))
        {
            try
            {
                config->set_%SETTER%( result["%ARGNAME%"].as<%TYPE%>() );
            }//try
            catch (const std::exception& e)
            {
                auto value = result["%ARGNAME%"].as<std::string>();
                std::cout << "[ERR] Error parsing option %ARGNAME% with value '" << value << "': " << e.what() << std::endl;
                if (!allowIncomplete)
                {
                    std::cout << usage(program).c_str() << std::endl;
                    delete config;
                    return nullptr;
                }//if
            }//catch
        }//if
"""

        code = ""

        # fill proto object
        start = False
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == pf_optional: # this parameter is optional
                            code += template \
                                    .replace("%ARGNAME%", link) \
                                    .replace("%TYPE%", self.__convertToCCType(token)) \
                                    .replace("%SETTER%", self.__convertToCCName(token.name))

        return code

    def __cxxoptsRepeatedParsing(self, tokens):
        template = """
        if (result.count("%ARGNAME%"))
        {
            try
            {
                auto list = result["%ARGNAME%"].as<%TYPE%>();
                for (const auto& el : list) {
                    config->add_%SETTER%(el);
                }//for
            }//try
            catch (const std::exception& e)
            {
                auto list = result["%ARGNAME%"].as<std::string>();
                std::string values;
                for (const auto& el : list) {
                    values += el;
                    values += " ";
                }//for
                std::cout << "[ERR] Error parsing option %ARGNAME% with value '" << values << "': " << e.what() << std::endl;
                if (!allowIncomplete)
                {
                    std::cout << usage(program).c_str() << std::endl;
                    delete config;
                    return nullptr;
                }//if
            }//catch
        }//if
"""

        code = ""

        # fill proto object
        start = False
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == pf_repeated: # this parameter is optional and may be specified multiple times
                            code += template \
                                    .replace("%ARGNAME%", link) \
                                    .replace("%TYPE%", self.__convertToCCType(token)) \
                                    .replace("%SETTER%", self.__convertToCCName(token.name))

        return code

    def __cxxoptsPositionalParsing(self, tokens):
        templateSingle = """
        if (result.count("positional") > %EXPECTEDPOS%)
        {
            try
            {
                auto list = result["positional"].as<std::vector<std::string>>();
                config->set_%SETTER%( %CONVERTER%(list[%EXPECTEDPOS%]) );
            }//try
            catch (std::exception& e)
            {
                auto list = result["positional"].as<std::vector<std::string>>();
                std::cout << "[ERR] Error parsing option %ARGNAME% with value '" << list[%EXPECTEDPOS%] << "': " << e.what() << std::endl;
                if (!allowIncomplete)
                {
                    std::cout << usage(program).c_str() << std::endl;
                    delete config;
                    return nullptr;
                }//if
            }//catch
        }
        else if (!allowIncomplete)
        {
            std::cout << "[ERR] '%ARGNAME%' is not set" << std::endl;
            std::cout << usage(program).c_str() << std::endl;
            delete config;
            return nullptr;
        }//if
"""

        templateRepeated = """
        if (result.count("positional") > %EXPECTEDPOS%)
        {
            try
            {
                auto list = result["positional"].as<std::vector<std::string>>();
                for (uint32_t i = %EXPECTEDPOS%; i < list.size(); ++i) {
                    config->add_%SETTER%( %CONVERTER%(list[i]) );
                }//for
            }//try
            catch (std::exception& e)
            {
                auto list = result["positional"].as<std::vector<std::string>>();
                std::cout << "[ERR] Error parsing option %ARGNAME% with value '" << list[%EXPECTEDPOS%] << "': " << e.what() << std::endl;
                if (!allowIncomplete)
                {
                    std::cout << usage(program).c_str() << std::endl;
                    delete config;
                    return nullptr;
                }//if
            }//catch
        }
        else if (!allowIncomplete)
        {
            std::cout << "[ERR] '%ARGNAME%' is not set" << std::endl;
            std::cout << usage(program).c_str() << std::endl;
            delete config;
            return nullptr;
        }//if
"""
        code = ""

        # fill proto object
        start = False
        pos = 0
        for token in tokens:
            if token.directive == pd_message and token.name == pa_main:
                start = True
            elif start:
                if token.directive == pd_end:
                    break
                elif token.directive == pd_field:
                    isLinks = self.__getToken(tokens, pd_message, pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) == 0: # process positional
                            if token.field == pf_repeated: # this parameter should have at least one arg present, nothing is processed afterwards
                                code += templateRepeated \
                                        .replace("%ARGNAME%", token.name.upper()) \
                                        .replace("%CONVERTER%", self.__converterFromString(token)) \
                                        .replace("%SETTER%", self.__convertToCCName(token.name)) \
                                        .replace("%EXPECTEDPOS%", str(pos))
                                break # all positional next values will be inside this arg
                            else: # no matter what is set, it is processed as required
                                code += templateSingle \
                                        .replace("%ARGNAME%", token.name.upper()) \
                                        .replace("%CONVERTER%", self.__converterFromString(token)) \
                                        .replace("%SETTER%", self.__convertToCCName(token.name)) \
                                        .replace("%EXPECTEDPOS%", str(pos))
                                pos += 1

        return code

if __name__ == "__main__":
    import sys

    print("[INF] Parse arguments")
    parser = ArgsParser()
    parser.parse(sys.argv[1:])

    print("[INF] Processing proto file " + parser.config.getProtoPath())
    path = parser.config.getProtoPath()
    generator = CppGenerator(path)
    generator.generate()
