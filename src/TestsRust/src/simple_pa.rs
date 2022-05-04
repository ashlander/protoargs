extern crate std;
extern crate clap;

pub mod simple_pa {

/// Configuration structure to hold all parsed arguments as strong typed entities
#[derive(Default)]
pub struct Config {
    /// Converted to --count
    count: Option<u64>,
    /// Converted to --configuration
    configuration: Option<String>,
    /// Converted to --flags, each encounter will be stored in list
    flags: Vec<bool>,
    /// Converted to --version
    version: Option<bool>,
    /// Converted to --help
    help: Option<bool>,
    /// Converted to -c short option
    c: Option<String>,
    /// Converted to r-underscore long option
    r_underscore: Option<String>,
    /// Converted to o-underscore long option
    o_underscore: Option<String>,
    /// Converted to a-underscore long option
    a_underscore: Vec<String>,
    /// Converted to s-quote-in-descr long option, "checking quotes"
    s_quote_in_descr: Option<String>,

}

impl Config {

    #[allow(dead_code)]
    pub fn has_count(&self) -> bool {
        !self.count.is_none()
    }

    #[allow(dead_code)]
    pub fn count(&self) -> u64 {
        self.count.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn has_configuration(&self) -> bool {
        !self.configuration.is_none()
    }

    #[allow(dead_code)]
    pub fn configuration(&self) -> String {
        self.configuration.clone().unwrap_or("".to_string())
    }

    #[allow(dead_code)]
    pub fn flags(&self) -> Vec<bool> {
        self.flags.clone()
    }

    #[allow(dead_code)]
    pub fn get_flags(&self, i: usize) -> bool {
        self.flags[i].clone()
    }

    #[allow(dead_code)]
    pub fn has_version(&self) -> bool {
        !self.version.is_none()
    }

    #[allow(dead_code)]
    pub fn version(&self) -> bool {
        self.version.clone().unwrap_or(false)
    }

    #[allow(dead_code)]
    pub fn has_help(&self) -> bool {
        !self.help.is_none()
    }

    #[allow(dead_code)]
    pub fn help(&self) -> bool {
        self.help.clone().unwrap_or(false)
    }

    #[allow(dead_code)]
    pub fn has_c(&self) -> bool {
        !self.c.is_none()
    }

    #[allow(dead_code)]
    pub fn c(&self) -> String {
        self.c.clone().unwrap_or("some value".to_string())
    }

    #[allow(dead_code)]
    pub fn has_r_underscore(&self) -> bool {
        !self.r_underscore.is_none()
    }

    #[allow(dead_code)]
    pub fn r_underscore(&self) -> String {
        self.r_underscore.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn has_o_underscore(&self) -> bool {
        !self.o_underscore.is_none()
    }

    #[allow(dead_code)]
    pub fn o_underscore(&self) -> String {
        self.o_underscore.clone().unwrap_or("".to_string())
    }

    #[allow(dead_code)]
    pub fn a_underscore(&self) -> Vec<String> {
        self.a_underscore.clone()
    }

    #[allow(dead_code)]
    pub fn get_a_underscore(&self, i: usize) -> String {
        self.a_underscore[i].clone()
    }

    #[allow(dead_code)]
    pub fn has_s_quote_in_descr(&self) -> bool {
        !self.s_quote_in_descr.is_none()
    }

    #[allow(dead_code)]
    pub fn s_quote_in_descr(&self) -> String {
        self.s_quote_in_descr.clone().unwrap_or("".to_string())
    }

}

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

    return command


                .arg(clap::Arg::new(r#"count"#)
                   .help(r#"Converted to --count {REQUIRED,type:uint64,default:"1"}"#)
                   .takes_value(true)
                   .required(true)
                   .multiple_occurrences(false)
                   .long(r#"count"#))

                .arg(clap::Arg::new(r#"configuration"#)
                   .help(r#"Converted to --configuration {OPTIONAL,type:string,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"configuration"#))

                .arg(clap::Arg::new(r#"flags"#)
                   .help(r#"Converted to --flags, each encounter will be stored in list {REPEATED,type:bool,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(true)
                   .long(r#"flags"#))

                .arg(clap::Arg::new(r#"version"#)
                   .help(r#"Converted to --version {OPTIONAL,type:bool,default:"false"}"#)
                   .takes_value(false)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"version"#))

                .arg(clap::Arg::new(r#"c"#)
                   .help(r#"Converted to -c short option {OPTIONAL,type:string,default:"some value"}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('c'))

                .arg(clap::Arg::new(r#"r-underscore"#)
                   .help(r#"Converted to r-underscore long option {REQUIRED,type:string,default:""}"#)
                   .takes_value(true)
                   .required(true)
                   .multiple_occurrences(false)
                   .long(r#"r-underscore"#))

                .arg(clap::Arg::new(r#"o-underscore"#)
                   .help(r#"Converted to o-underscore long option {OPTIONAL,type:string,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"o-underscore"#))

                .arg(clap::Arg::new(r#"a-underscore"#)
                   .help(r#"Converted to a-underscore long option {REPEATED,type:string,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(true)
                   .long(r#"a-underscore"#))

                .arg(clap::Arg::new(r#"s-quote-in-descr"#)
                   .help(r#"Converted to s-quote-in-descr long option, "checking quotes" {OPTIONAL,type:string,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"s-quote-in-descr"#))
               ;
}

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

    let has_count = matches.is_present("count");
    if !allow_incomplete && !has_count {
        return Err("Required 'count' is missing".to_string());
    }
    config.count = matches.value_of("count").map(|o| o.parse::<u64>().ok()).flatten();
    if has_count && !config.has_count() {
        let err = format!("Type 'u64' conversion failed for 'count' with value '{}'", matches.value_of("count").unwrap());
        return Err(err);
    }

    let has_configuration = matches.is_present("configuration");
    config.configuration = matches.value_of("configuration").map(|o| o.parse::<String>().ok()).flatten();
    if has_configuration && !config.has_configuration() {
        let err = format!("Type 'String' conversion failed for 'configuration' with value '{}'", matches.value_of("configuration").unwrap());
        return Err(err);
    }

    let count_flags : usize = matches.occurrences_of("flags").try_into().unwrap();
    config.flags = matches.values_of("flags")
        .map(|vals| vals.map(|o| o.parse::<bool>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_flags != config.flags.len() {
        return Err("Type 'bool' conversion failed for 'flags'".to_string());
    }

    let has_version = matches.is_present("version");
    if has_version && matches.value_of("version").is_none() {
        config.version = Some(true);
    } else {
        config.version = matches.value_of("version").map(|o| o.parse::<bool>().ok()).flatten();
        if has_version && !config.has_version() {
            let err = format!("Type 'bool' conversion failed for 'version' with value '{}'", matches.value_of("version").unwrap());
            return Err(err);
        }
    }

    let has_help = matches.is_present("help");
    if has_help && matches.value_of("help").is_none() {
        config.help = Some(true);
    } else {
        config.help = matches.value_of("help").map(|o| o.parse::<bool>().ok()).flatten();
        if has_help && !config.has_help() {
            let err = format!("Type 'bool' conversion failed for 'help' with value '{}'", matches.value_of("help").unwrap());
            return Err(err);
        }
    }

    let has_c = matches.is_present("c");
    config.c = matches.value_of("c").map(|o| o.parse::<String>().ok()).flatten();
    if has_c && !config.has_c() {
        let err = format!("Type 'String' conversion failed for 'c' with value '{}'", matches.value_of("c").unwrap());
        return Err(err);
    }

    let has_r_underscore = matches.is_present("r-underscore");
    if !allow_incomplete && !has_r_underscore {
        return Err("Required 'r-underscore' is missing".to_string());
    }
    config.r_underscore = matches.value_of("r-underscore").map(|o| o.parse::<String>().ok()).flatten();
    if has_r_underscore && !config.has_r_underscore() {
        let err = format!("Type 'String' conversion failed for 'r-underscore' with value '{}'", matches.value_of("r-underscore").unwrap());
        return Err(err);
    }

    let has_o_underscore = matches.is_present("o-underscore");
    config.o_underscore = matches.value_of("o-underscore").map(|o| o.parse::<String>().ok()).flatten();
    if has_o_underscore && !config.has_o_underscore() {
        let err = format!("Type 'String' conversion failed for 'o-underscore' with value '{}'", matches.value_of("o-underscore").unwrap());
        return Err(err);
    }

    let count_a_underscore : usize = matches.occurrences_of("a-underscore").try_into().unwrap();
    config.a_underscore = matches.values_of("a-underscore")
        .map(|vals| vals.map(|o| o.parse::<String>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_a_underscore != config.a_underscore.len() {
        return Err("Type 'String' conversion failed for 'a-underscore'".to_string());
    }

    let has_s_quote_in_descr = matches.is_present("s-quote-in-descr");
    config.s_quote_in_descr = matches.value_of("s-quote-in-descr").map(|o| o.parse::<String>().ok()).flatten();
    if has_s_quote_in_descr && !config.has_s_quote_in_descr() {
        let err = format!("Type 'String' conversion failed for 's-quote-in-descr' with value '{}'", matches.value_of("s-quote-in-descr").unwrap());
        return Err(err);
    }


    Ok(config)
}

}