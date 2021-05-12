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

# c++ types
cc_float = "float"
cc_double = "double"
cc_int32 = "int32_t"
cc_uint32 = "uint32_t"
cc_int64 = "int64_t"
cc_uint64 = "uint64_t"
cc_bool = "bool"
cc_string = "std::string"

# END GLOBALS ###################################3

class Generator:

    __path = "" # path to proto file
    __pbhName = ""  # name of protobuf header file for include
    __ccPath = "" # path to source file
    __hPath = ""  # path to header file
    __cc = "" # source file content
    __h = ""  # header content

    def __init__(self, path, dst):
        self.__path = path
        filename = os.path.splitext( os.path.basename(path) )[0]
        base = os.path.join(dst, filename)
        self.__hPath = base + ".pa.h"
        self.__ccPath = base + ".pa.cc"
        self.__pbhName = filename + ".pb.h"

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

    # parse proto file and generate c++ files
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
        if protoType == pt_float:
            ccType = cc_float
        if protoType == pt_double:
            ccType = cc_double

        # value may be repeated
        if token.field == paTokenizer.pf_repeated:
            ccType = "std::vector<" + ccType + ">"

        return ccType

    def __converterFromString(self, token):
        stringConverter = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            stringConverter = "std::stoi"
        if protoType == pt_uint32:
            stringConverter = "std::stoi"
        if protoType == pt_int64:
            stringConverter = "std::stoll"
        if protoType == pt_uint64:
            stringConverter = "std::stoll"
        if protoType == pt_float:
            stringConverter = "std::stof"
        if protoType == pt_double:
            stringConverter = "std::stof"
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
            if token.directive == paTokenizer.pd_package:
                logging.debug(str(token))
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
            if token.directive == paTokenizer.pd_package:
                logging.debug(str(token))
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
    cxxopts::Options options(program, "%DESCRIPTION%");
"""
        token = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_main)
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

        # add dummy positional long args, in order to preserve usage output style
        for token in positional:
            logging.debug("Create dummy positional field name as long arg name: " + str(token))
            # add cxxopts option
            prefix = "dummy-"
            code += "       "
            code += template \
                    .replace("%OPTIONS%",prefix + self.__convertToArgName(token.name)) \
                    .replace("%DESCRIPTION%",token.description) \
                    .replace("%PTYPE%", token.type) \
                    .replace("%TYPE%", self.__convertToCCType(token)) \
                    .replace("%ARGNAME%", token.name) \
                    .replace("%FREQUENCY%", paTokenizer.pf_required.upper()) \

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
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 0:
                            # add all links as options
                            logging.debug("links found for: " + str(token) + "\n" + str(links))
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
                            logging.debug("positional arg found: " + str(token))
                            positional.append(token)
                    else:
                        logging.debug("convert main protoargs field name into long arg name: " + str(token))
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
                    logging.warn("unknown token inside protoargs structure: " + str(token))

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
                if pos.field == paTokenizer.pf_repeated:
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
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == paTokenizer.pf_required: # this parameter should be present
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
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == paTokenizer.pf_optional: # this parameter is optional
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
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    link = self.__convertToCCName(token.name) # default link
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) > 1:
                            link = self.__convertToArgName(links[1].name) # take long option if available
                        elif len(links) > 0:
                            link = self.__convertToArgName(links[0].name)

                    if (isLinks and len(links) > 0) or not isLinks: # avoid positional
                        if token.field == paTokenizer.pf_repeated: # this parameter is optional and may be specified multiple times
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
            if token.directive == paTokenizer.pd_message and token.name == paTokenizer.pa_main:
                start = True
            elif start:
                if token.directive == paTokenizer.pd_end:
                    break
                elif token.directive == paTokenizer.pd_field:
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = self.__getLinks(tokens, token.name)
                        if len(links) == 0: # process positional
                            if token.field == paTokenizer.pf_repeated: # this parameter should have at least one arg present, nothing is processed afterwards
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

