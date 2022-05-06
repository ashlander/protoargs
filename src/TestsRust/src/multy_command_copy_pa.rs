extern crate std;
extern crate clap;

pub mod multy_command_copy_pa {

/// Configuration structure to hold all parsed arguments as strong typed entities
#[derive(Default)]
pub struct Config {
    /// Recursive copy
    recursive: Option<bool>,
    /// Path to source path
    src: Option<String>,
    /// Path to destination path
    dst: Option<String>,

}

impl Config {

    #[allow(dead_code)]
    pub fn has_recursive(&self) -> bool {
        !self.recursive.is_none()
    }

    #[allow(dead_code)]
    pub fn recursive(&self) -> bool {
        self.recursive.clone().unwrap_or(false)
    }

    #[allow(dead_code)]
    pub fn has_src(&self) -> bool {
        !self.src.is_none()
    }

    #[allow(dead_code)]
    pub fn src(&self) -> String {
        self.src.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn has_dst(&self) -> bool {
        !self.dst.is_none()
    }

    #[allow(dead_code)]
    pub fn dst(&self) -> String {
        self.dst.clone().unwrap()
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


                .arg(clap::Arg::new(r#"recursive"#)
                   .help(r#"Recursive copy {OPTIONAL,type:bool,default:"false"}"#)
                   .takes_value(false)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('r')
                   .long(r#"recursive"#))

        .arg(clap::Arg::new(r#"SRC"#)
           .help(r#"Path to source path {REQUIRED,type:string}"#)
           .required(true)
           .index(1)
           .multiple_occurrences(false))


        .arg(clap::Arg::new(r#"DST"#)
           .help(r#"Path to destination path {REQUIRED,type:string}"#)
           .required(true)
           .index(2)
           .multiple_occurrences(false))

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

    let has_recursive = matches.is_present("recursive");
    if has_recursive && matches.value_of("recursive").is_none() {
        config.recursive = Some(true);
    } else {
        config.recursive = matches.value_of("recursive").map(|o| o.parse::<bool>().ok()).flatten();
        if has_recursive && !config.has_recursive() {
            let err = format!("Type 'bool' conversion failed for 'recursive' with value '{}'", matches.value_of("recursive").unwrap());
            return Err(err);
        }
    }

    let has_src = matches.is_present("SRC");
    if !allow_incomplete && !has_src {
        return Err("Required 'SRC' is missing".to_string());
    }
    config.src = matches.value_of("SRC").map(|o| o.parse::<String>().ok()).flatten();
    if has_src && !config.has_src() {
        let err = format!("Type 'String' conversion failed for 'SRC' with value '{}'", matches.value_of("SRC").unwrap());
        return Err(err);
    }

    let has_dst = matches.is_present("DST");
    if !allow_incomplete && !has_dst {
        return Err("Required 'DST' is missing".to_string());
    }
    config.dst = matches.value_of("DST").map(|o| o.parse::<String>().ok()).flatten();
    if has_dst && !config.has_dst() {
        let err = format!("Type 'String' conversion failed for 'DST' with value '{}'", matches.value_of("DST").unwrap());
        return Err(err);
    }


    Ok(config)
}

}