extern crate std;
extern crate clap;

pub mod multy_command_create_pa {

/// Configuration structure to hold all parsed arguments as strong typed entities
#[derive(Default)]
pub struct Config {
    /// Size of the file
    size: Option<u64>,
    /// Path to file to create
    path: Option<String>,

}

impl Config {

    #[allow(dead_code)]
    pub fn has_size(&self) -> bool {
        !self.size.is_none()
    }

    #[allow(dead_code)]
    pub fn size(&self) -> u64 {
        self.size.clone().unwrap_or(0)
    }

    #[allow(dead_code)]
    pub fn has_path(&self) -> bool {
        !self.path.is_none()
    }

    #[allow(dead_code)]
    pub fn path(&self) -> String {
        self.path.clone().unwrap()
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


                .arg(clap::Arg::new(r#"size"#)
                   .help(r#"Size of the file {OPTIONAL,type:uint64,default:"0"}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('s')
                   .long(r#"size"#))

        .arg(clap::Arg::new(r#"PATH"#)
           .help(r#"Path to file to create {REQUIRED,type:string}"#)
           .required(true)
           .index(1)
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

    let has_size = matches.is_present("size");
    config.size = matches.value_of("size").map(|o| o.parse::<u64>().ok()).flatten();
    if has_size && !config.has_size() {
        let err = format!("Type 'u64' conversion failed for 'size' with value '{}'", matches.value_of("size").unwrap());
        return Err(err);
    }

    let has_path = matches.is_present("PATH");
    if !allow_incomplete && !has_path {
        return Err("Required 'PATH' is missing".to_string());
    }
    config.path = matches.value_of("PATH").map(|o| o.parse::<String>().ok()).flatten();
    if has_path && !config.has_path() {
        let err = format!("Type 'String' conversion failed for 'PATH' with value '{}'", matches.value_of("PATH").unwrap());
        return Err(err);
    }


    Ok(config)
}

}