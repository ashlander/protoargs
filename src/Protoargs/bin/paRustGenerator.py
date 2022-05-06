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

# rust types
rust_float = "f32"
rust_double = "f64"
rust_int32 = "i32"
rust_uint32 = "u32"
rust_int64 = "i64"
rust_uint64 = "u64"
rust_bool = "bool"
rust_string = "String"

# END GLOBALS ###################################3

class Generator:

    __path = "" # path to proto file
    __rustPath = "" # path to source file
    __mod = "" # rust module name
    __rust = "" # source file content

    def __init__(self, path, dst):
        self.__path = path
        filename = os.path.splitext( os.path.basename(path) )[0]
        base = os.path.join(dst, filename)
        self.__rustPath = base + "_pa.rs"
        self.__mod = filename + "_pa"

    def getSourceFileData(self):
        return self.__rust

    def getSourceFilePath(self):
        return self.__rustPath

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

    # parse proto file and generate rust files
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
                self.__rust = self.__generateSourceFromTokens(tokens)

                # save code to files
                self.__saveFileData( self.getSourceFilePath(), self.__rust )

        return data

    # convert protobuf config names into c code names
    def __convertToRustName(self, name):
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

    # convert protobuf config types into rust types
    def __convertToRustType(self, token):
        pyType = token.type # if missing use original

        # get correct type
        protoType = token.type
        if protoType == pt_int32:
            pyType = rust_int32
        if protoType == pt_uint32:
            pyType = rust_uint32
        if protoType == pt_int64:
            pyType = rust_int64
        if protoType == pt_uint64:
            pyType = rust_uint64
        if protoType == pt_bool:
            pyType = rust_bool
        if protoType == pt_string:
            pyType = rust_string
        if protoType == pt_float:
            pyType = rust_float
        if protoType == pt_double:
            pyType = rust_double

        return pyType

    def __convertToDefaultValue(self, token):
        if not token.value:
            return ""
        return (r'r"""' + token.value + r'"""' if token.type == pt_string else token.value).replace("true", "True").replace("false", "False")

    # generate rust source file content
    def __generateSourceFromTokens(self, tokens):
        head = """extern crate std;
extern crate clap;

"""
        head += "pub mod " + self.__mod + " {\n";

        tail = "\n}"
        body = ""

        # add configuration structure to store typed values
        body += """
/// Configuration structure to hold all parsed arguments as strong typed entities
#[derive(Default)]
pub struct Config {
"""
        # register fields
        body += self.__clapStructureFields(tokens)

        body += """
}
"""

        # add configuration structure implementation
        body += """
impl Config {
"""
        # register fields
        body += self.__clapStructureImpl(tokens)

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
/// * `description` - Description to display in help message
///
/// returns Command instance ready to do parsing
#[allow(dead_code)]
pub fn prepare_options<'a>(program: &'a str, description: &'a str) -> clap::Command<'a> {
    let command = clap::Command::new(program)
                    .global_setting(clap::AppSettings::DeriveDisplayOrder)
                    .about(description);

    return prepare_options_ext(command);
}

/// Options preparation, may be used to append arguments to existing command instance
///
/// # Arguments
///
/// * `command` - Command instance to update
///
/// returns Command instance ready to do parsing
#[allow(dead_code)]
pub fn prepare_options_ext<'a>(command: clap::Command<'a>) -> clap::Command<'a> {
"""
        # register arguments
        body += self.__clapProgramDescription(tokens)

        body += self.__clapProgramOptions(tokens)

        body += self.__clapPositionalOptions(tokens)

        body += """               ;
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
#[allow(dead_code)]
pub fn usage(program: &str, description: &str) -> String {
    prepare_options(program, description).render_usage()
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
#[allow(dead_code)]
pub fn parse(program: &str, description: &str) -> Result<Config, String> {
    let args: Vec<String> = std::env::args().collect();
    parse_vec(program, &args, description)
}

/// Parse command line arguments, and return filled configuration
/// Good for unit testing, as it will not exit program on failure
/// and will return error string instead
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments
/// * `description` - Description to display in help message
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_debug(program: &str, args: &[&str], description: &str) -> Result<Config, String> {
    parse_command(args, prepare_options(program, description).ignore_errors(true), false)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments as string vector
/// * `description` - Description to display in help message
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_vec(program: &str, args: &Vec<String>, description: &str) -> Result<Config, String> {
    let sargs : Vec<_> = args.iter().map(String::as_str).collect();
    parse_command(&sargs[..], prepare_options(program, description), false)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments as str slice
/// * `description` - Description to display in help message
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_str(program: &str, args: &[&str], description: &str) -> Result<Config, String> {
    parse_command(args, prepare_options(program, description), false)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments as str slice
/// * `description` - Description to display in help message
/// * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
/// wrong type cast will produce error anyway
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_ext(program: &str, args: &[&str], description: &str, allow_incomplete: bool) -> Result<Config, String> {
    parse_command(args, prepare_options(program, description), allow_incomplete)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `args` - Command line arguments as str slice
/// * `command` - Existing command instance
/// * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
/// wrong type cast will produce error anyway
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_command(args: &[&str], command: clap::Command, allow_incomplete: bool) -> Result<Config, String> {
    let matches = (if allow_incomplete { command.ignore_errors(true) } else { command } ).get_matches_from(args);
    parse_matches(&matches, allow_incomplete)
}

/// Post parse processing to fill in configuration structure
/// If you are up to multi commands e.g. 'git [init, commit, etc]'
/// this will be helpful
///
/// # Arguments
///
/// * `matches` - Matches instance
/// * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
/// wrong type cast will produce error anyway
///
/// returns Result with configuration structure, or error message
#[allow(dead_code)]
pub fn parse_matches(matches: &clap::ArgMatches, allow_incomplete: bool) -> Result<Config, String> {
    let mut config = Config { ..Default::default() };

"""

        # register fields
        body += self.__clapStructureFill(tokens)

        body += """
    Ok(config)
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

    def __clapStructureFields(self, tokens):
        template = """    /// %DESCRIPTION%
    %NAME%: %TYPE%,\n"""
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
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        for link in links:
                            if link.name == "h" or link.name == "help": # exclude predefined args
                                append = False
                                break

                    if append:
                        logging.debug("Create struct field name: " + str(token))
                        rustType = self.__convertToRustType(token)
                        if token.field == paTokenizer.pf_repeated:
                            rustType = "Vec<" + rustType + ">"
                        elif token.field == paTokenizer.pf_optional:
                            rustType = "Option<" + rustType + ">"
                        elif token.field == paTokenizer.pf_required:
                            rustType = "Option<" + rustType + ">"

                        code += template \
                                .replace("%NAME%", self.__convertToRustName(token.name)) \
                                .replace("%TYPE%", rustType) \
                                .replace("%DESCRIPTION%", token.description)

        return code

    def __clapStructureImpl(self, tokens):
        templateOptional = r"""
    #[allow(dead_code)]
    pub fn has_%NAME%(&self) -> bool {
        !self.%NAME%.is_none()
    }

    #[allow(dead_code)]
    pub fn %NAME%(&self) -> %TYPE% {
        self.%NAME%.clone().unwrap_or(%DEFAULT%)
    }
"""

        templateOptionalNoDefault = r"""
    #[allow(dead_code)]
    pub fn has_%NAME%(&self) -> bool {
        !self.%NAME%.is_none()
    }

    #[allow(dead_code)]
    pub fn %NAME%(&self) -> %TYPE% {
        self.%NAME%.clone().unwrap_or_default()
    }
"""

        templateRequired = r"""
    #[allow(dead_code)]
    pub fn has_%NAME%(&self) -> bool {
        !self.%NAME%.is_none()
    }

    #[allow(dead_code)]
    pub fn %NAME%(&self) -> %TYPE% {
        self.%NAME%.clone().unwrap()
    }
"""

        templateRepeated = r"""
    #[allow(dead_code)]
    pub fn %NAME%(&self) -> Vec<%TYPE%> {
        self.%NAME%.clone()
    }

    #[allow(dead_code)]
    pub fn get_%NAME%(&self, i: usize) -> %TYPE% {
        self.%NAME%[i].clone()
    }
"""

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
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        for link in links:
                            if link.name == "h" or link.name == "help": # exclude predefined args
                                append = False
                                break

                    if append:
                        logging.debug("Fill struct field name: " + str(token))
                        rustType = self.__convertToRustType(token)

                        template = templateOptional
                        if token.field == paTokenizer.pf_repeated:
                            template = templateRepeated
                        elif token.field == paTokenizer.pf_required:
                            template = templateRequired;

                        default = token.value
                        if (token.type == pt_string):
                            default = "\"" + token.value + "\".to_string()"
                        elif (template == templateOptional and len(token.value) == 0):
                            template = templateOptionalNoDefault

                        code += template \
                                .replace("%NAME%", self.__convertToRustName(token.name)) \
                                .replace("%DEFAULT%", default) \
                                .replace("%OPTION%", self.__convertToArgName(token.name)) \
                                .replace("%TYPE%", rustType)

        return code


    def __clapStructureFill(self, tokens):
        templateOptional = r"""    let has_%NAME% = matches.is_present("%OPTION%");
    config.%NAME% = matches.value_of("%OPTION%").map(|o| o.parse::<%TYPE%>().ok()).flatten();
    if has_%NAME% && !config.has_%NAME%() {
        let err = format!("Type '%TYPE%' conversion failed for '%OPTION%' with value '{}'", matches.value_of("%OPTION%").unwrap());
        return Err(err);
    }

"""

        templateBoolOptional = r"""    let has_%NAME% = matches.is_present("%OPTION%");
    if has_%NAME% && matches.value_of("%OPTION%").is_none() {
        config.%NAME% = Some(true);
    } else {
        config.%NAME% = matches.value_of("%OPTION%").map(|o| o.parse::<%TYPE%>().ok()).flatten();
        if has_%NAME% && !config.has_%NAME%() {
            let err = format!("Type '%TYPE%' conversion failed for '%OPTION%' with value '{}'", matches.value_of("%OPTION%").unwrap());
            return Err(err);
        }
    }

"""

        templateRequired = r"""    let has_%NAME% = matches.is_present("%OPTION%");
    if !allow_incomplete && !has_%NAME% {
        return Err("Required '%OPTION%' is missing".to_string());
    }
    config.%NAME% = matches.value_of("%OPTION%").map(|o| o.parse::<%TYPE%>().ok()).flatten();
    if has_%NAME% && !config.has_%NAME%() {
        let err = format!("Type '%TYPE%' conversion failed for '%OPTION%' with value '{}'", matches.value_of("%OPTION%").unwrap());
        return Err(err);
    }

"""

        templateBoolRequired = r"""    let has_%NAME% = matches.is_present("%OPTION%");
    if !allow_incomplete && !has_%NAME% {
        return Err("Required '%OPTION%' is missing".to_string());
    }
    if has_%NAME% && matches.value_of("%OPTION%").is_none() {
        config.%NAME% = Some(true);
    } else {
        config.%NAME% = matches.value_of("%OPTION%").map(|o| o.parse::<%TYPE%>().ok()).flatten();
        if has_%NAME% && !config.has_%NAME%() {
            let err = format!("Type '%TYPE%' conversion failed for '%OPTION%' with value '{}'", matches.value_of("%OPTION%").unwrap());
            return Err(err);
        }
    }

"""

        templateRepeated = r"""    let count_%NAME% : usize = matches.occurrences_of("%OPTION%").try_into().unwrap();
    config.%NAME% = matches.values_of("%OPTION%")
        .map(|vals| vals.map(|o| o.parse::<%TYPE%>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_%NAME% != config.%NAME%.len() {
        return Err("Type '%TYPE%' conversion failed for '%OPTION%'".to_string());
    }

"""

        templateRepeatedPositional = r"""    let count_%NAME% : usize = matches.occurrences_of("%OPTION%").try_into().unwrap();
    if !allow_incomplete && count_%NAME% == 0 {
        return Err("Required at least one positional '%OPTION%'".to_string());
    }
    config.%NAME% = matches.values_of("%OPTION%")
        .map(|vals| vals.map(|o| o.parse::<%TYPE%>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_%NAME% != config.%NAME%.len() {
        return Err("Type '%TYPE%' conversion failed for '%OPTION%'".to_string());
    }

"""
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
                    positional = False
                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) == 0:
                            positional = True
                        for link in links:
                            if link.name == "h" or link.name == "help": # exclude predefined args
                                append = False
                                break

                    if append:
                        logging.debug("Fill struct field name: " + str(token))
                        rustType = self.__convertToRustType(token)

                        template = templateOptional
                        if positional and token.field == paTokenizer.pf_repeated:
                            template = templateRepeatedPositional
                        elif token.field == paTokenizer.pf_repeated:
                            template = templateRepeated
                        elif token.type == pt_bool and token.field == paTokenizer.pf_optional:
                            template = templateBoolOptional
                        elif token.type == pt_bool and token.field == paTokenizer.pf_required:
                            template = templateBoolRequired
                        elif token.field == paTokenizer.pf_required:
                            template = templateRequired

                        code += template \
                                .replace("%NAME%", self.__convertToRustName(token.name)) \
                                .replace("%OPTION%", self.__convertToArgName(token.name)) \
                                .replace("%TYPE%", rustType)

        return code



    def __clapProgramDescription(self, tokens):
        code = """
    return command
"""
        token = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_main)
        if token.valid():
            code = code.replace("%DESCRIPTION%", token.description)

        code += "\n"
        return code

    def __clapPositionalOptions(self, tokens):
        template = r"""
        .arg(clap::Arg::new(r#"%OPTIONS%"#)
           .help(r#"%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%}"#)
           .required(true)
           .index(%INDEX%)
           .multiple_occurrences(%REPEATED%))
"""
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
        index = 1;
        for token in positional:
            logging.debug("Create positional field name: " + str(token))
            code += template \
                    .replace("%OPTIONS%", self.__convertToArgName(token.name)) \
                    .replace("%DESCRIPTION%", token.description) \
                    .replace("%PTYPE%", token.type) \
                    .replace("%TYPE%", self.__convertToRustType(token)) \
                    .replace("%ARGNAME%", token.name) \
                    .replace("%FREQUENCY%", paTokenizer.pf_required.upper()) \
                    .replace("%NARGS%", (r'nargs="+",' if token.field == paTokenizer.pf_repeated else "") ) \
                    .replace("%INDEX%", str(index)) \
                    .replace("%REPEATED%", \
                    ("true" if token.field == paTokenizer.pf_repeated else "false") )

            code += "\n"
            index += 1

        return code

    def __clapProgramOptions(self, tokens):
        template = r"""
                .arg(clap::Arg::new(r#"%OPTIONS%"#)
                   .help(r#"%DESCRIPTION% {%FREQUENCY%,type:%PTYPE%,default:"%DEFAULT%"}"#)
                   .takes_value(%WITHVALUE%)
                   .required(%REQUIRED%)
                   .multiple_occurrences(%REPEATED%)"""

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

                    isLinks = self.__getToken(tokens, paTokenizer.pd_message, paTokenizer.pa_links).valid()
                    if isLinks:
                        links = sorted(self.__getLinks(tokens, token.name), key=lambda link: link.name)
                        if len(links) > 0:
                            # add all links as options
                            logging.debug("links found for: " + str(token) + "\n" + str(links))
                            options = ""
                            for link in links:
                                if link.name != "h" and link.name != "help": # exclude predefined args
                                    if len(link.name) == 1:
                                        options += "\n                   .short('" + self.__convertToArgName(link.name) + "')" # convert into args
                                    else:
                                        options += "\n                   .long(r#\"" + self.__convertToArgName(link.name) + "\"#)" # convert into args
                                else:
                                    logging.warn("'" + link.name + "' conflicts with predefined argument");

                            if options:
                                code += t \
                                        .replace("%OPTIONS%", self.__convertToArgName(token.name)) \
                                        .replace("%DESCRIPTION%",token.description) \
                                        .replace("%PTYPE%", token.type) \
                                        .replace("%ARGNAME%", token.name) \
                                        .replace("%FREQUENCY%", token.field.upper()) \
                                        .replace("%DEFAULT%", token.value) \
                                        .replace("%TYPE%", \
                                        (", type=" + self.__convertToRustType(token) if token.type != pt_bool else "") ) \
                                        .replace("%REQUIRED%", \
                                        ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                        .replace("%REPEATED%", \
                                        ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                        .replace("%WITHVALUE%", \
                                        ("true" if token.type != pt_bool else "false") ) \

                                code += options
                                code += ")\n"
                        else:
                            logging.debug("positional arg found: " + str(token))
                            positional.append(token)
                    else:
                        if token.name != "h" and token.name != "help": # exclude predefined args
                            logging.debug("convert main protoargs field name into long arg name: " + str(token))
                            code += t \
                                    .replace("%OPTIONS%", self.__convertToArgName(token.name) ) \
                                    .replace("%DESCRIPTION%",token.description) \
                                    .replace("%PTYPE%", token.type) \
                                    .replace("%ARGNAME%", token.name) \
                                    .replace("%FREQUENCY%", token.field.upper()) \
                                    .replace("%DEFAULT%", token.value) \
                                    .replace("%TYPE%", \
                                    (", type=" + self.__convertToRustType(token) if token.type != pt_bool else "") ) \
                                    .replace("%REQUIRED%", \
                                    ("true" if token.field == paTokenizer.pf_required else "false") ) \
                                    .replace("%REPEATED%", \
                                    ("true" if token.field == paTokenizer.pf_repeated else "false") ) \
                                    .replace("%WITHVALUE%", \
                                    ("true" if token.type != pt_bool or token.field == paTokenizer.pf_repeated else "false") ) \

                            if len(token.name) == 1:
                                code += "\n                   .short('" + self.__convertToArgName(token.name) + "')" # convert into args
                            else:
                                code += "\n                   .long(r#\"" + self.__convertToArgName(token.name) + "\"#)" # convert into args

                            code += ")\n"
                        else:
                            logging.warn("'" + token.name + "' conflicts with predefined argument");
                else:
                    logging.warn("unknown token inside protoargs structure: " + str(token))

        return code

