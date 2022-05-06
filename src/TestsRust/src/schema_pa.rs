extern crate std;
extern crate clap;

pub mod schema_pa {

/// Configuration structure to hold all parsed arguments as strong typed entities
#[derive(Default)]
pub struct Config {
    /// String param option with default value. Note: this comment will be taken as description
    parama: Option<String>,
    /// Integer param with default value
    paramb: Option<u32>,
    /// Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway
    paramc: Option<i32>,
    /// Float param without default value
    paramd: Option<f32>,
    /// String param which should be anyway
    parame: Option<String>,
    /// Integer param which may encounter multiple times
    paramf: Vec<i32>,
    /// Positional integer param, positional param is always \"required\"
    paramg: Option<u64>,
    /// Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false
    p_a_r_a_m_g_2: Option<bool>,
    /// Boolean arg with default value (despite it is declared after positional args, that is not a problem)
    param_i: Option<bool>,
    /// Boolean arg without default value
    param_j: Option<bool>,
    /// Positional float param
    param_float: Option<f32>,
    /// Positional double param
    param_double: Option<f64>,
    /// Positional repeating string params, there may be only one repeating positional param
    paramh: Vec<String>,
    /// Float param
    paramfloat: Option<f32>,
    /// Double param
    paramdouble: Option<f64>,

}

impl Config {

    #[allow(dead_code)]
    pub fn has_parama(&self) -> bool {
        !self.parama.is_none()
    }

    #[allow(dead_code)]
    pub fn parama(&self) -> String {
        self.parama.clone().unwrap_or("// tricky default value".to_string())
    }

    #[allow(dead_code)]
    pub fn has_paramb(&self) -> bool {
        !self.paramb.is_none()
    }

    #[allow(dead_code)]
    pub fn paramb(&self) -> u32 {
        self.paramb.clone().unwrap_or(10)
    }

    #[allow(dead_code)]
    pub fn has_paramc(&self) -> bool {
        !self.paramc.is_none()
    }

    #[allow(dead_code)]
    pub fn paramc(&self) -> i32 {
        self.paramc.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn has_paramd(&self) -> bool {
        !self.paramd.is_none()
    }

    #[allow(dead_code)]
    pub fn paramd(&self) -> f32 {
        self.paramd.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn has_parame(&self) -> bool {
        !self.parame.is_none()
    }

    #[allow(dead_code)]
    pub fn parame(&self) -> String {
        self.parame.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn paramf(&self) -> Vec<i32> {
        self.paramf.clone()
    }

    #[allow(dead_code)]
    pub fn get_paramf(&self, i: usize) -> i32 {
        self.paramf[i].clone()
    }

    #[allow(dead_code)]
    pub fn has_paramg(&self) -> bool {
        !self.paramg.is_none()
    }

    #[allow(dead_code)]
    pub fn paramg(&self) -> u64 {
        self.paramg.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn has_p_a_r_a_m_g_2(&self) -> bool {
        !self.p_a_r_a_m_g_2.is_none()
    }

    #[allow(dead_code)]
    pub fn p_a_r_a_m_g_2(&self) -> bool {
        self.p_a_r_a_m_g_2.clone().unwrap()
    }

    #[allow(dead_code)]
    pub fn has_param_i(&self) -> bool {
        !self.param_i.is_none()
    }

    #[allow(dead_code)]
    pub fn param_i(&self) -> bool {
        self.param_i.clone().unwrap_or(true)
    }

    #[allow(dead_code)]
    pub fn has_param_j(&self) -> bool {
        !self.param_j.is_none()
    }

    #[allow(dead_code)]
    pub fn param_j(&self) -> bool {
        self.param_j.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn has_param_float(&self) -> bool {
        !self.param_float.is_none()
    }

    #[allow(dead_code)]
    pub fn param_float(&self) -> f32 {
        self.param_float.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn has_param_double(&self) -> bool {
        !self.param_double.is_none()
    }

    #[allow(dead_code)]
    pub fn param_double(&self) -> f64 {
        self.param_double.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn paramh(&self) -> Vec<String> {
        self.paramh.clone()
    }

    #[allow(dead_code)]
    pub fn get_paramh(&self, i: usize) -> String {
        self.paramh[i].clone()
    }

    #[allow(dead_code)]
    pub fn has_paramfloat(&self) -> bool {
        !self.paramfloat.is_none()
    }

    #[allow(dead_code)]
    pub fn paramfloat(&self) -> f32 {
        self.paramfloat.clone().unwrap_or_default()
    }

    #[allow(dead_code)]
    pub fn has_paramdouble(&self) -> bool {
        !self.paramdouble.is_none()
    }

    #[allow(dead_code)]
    pub fn paramdouble(&self) -> f64 {
        self.paramdouble.clone().unwrap_or_default()
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


                .arg(clap::Arg::new(r#"paramA"#)
                   .help(r#"String param option with default value. Note: this comment will be taken as description {OPTIONAL,type:string,default:"// tricky default value"}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('a')
                   .long(r#"a-long-param"#))

                .arg(clap::Arg::new(r#"paramB"#)
                   .help(r#"Integer param with default value {OPTIONAL,type:uint32,default:"10"}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"b-long-param"#))

                .arg(clap::Arg::new(r#"paramC"#)
                   .help(r#"Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway {OPTIONAL,type:int32,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('c')
                   .long(r#"c-long-param"#))

                .arg(clap::Arg::new(r#"paramD"#)
                   .help(r#"Float param without default value {OPTIONAL,type:float,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"d-long-param"#))

                .arg(clap::Arg::new(r#"paramE"#)
                   .help(r#"String param which should be anyway {REQUIRED,type:string,default:""}"#)
                   .takes_value(true)
                   .required(true)
                   .multiple_occurrences(false)
                   .short('e'))

                .arg(clap::Arg::new(r#"paramF"#)
                   .help(r#"Integer param which may encounter multiple times {REPEATED,type:int32,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(true)
                   .short('f'))

                .arg(clap::Arg::new(r#"param-I"#)
                   .help(r#"Boolean arg with default value (despite it is declared after positional args, that is not a problem) {OPTIONAL,type:bool,default:"true"}"#)
                   .takes_value(false)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('i'))

                .arg(clap::Arg::new(r#"param-J"#)
                   .help(r#"Boolean arg without default value {OPTIONAL,type:bool,default:""}"#)
                   .takes_value(false)
                   .required(false)
                   .multiple_occurrences(false)
                   .long(r#"j-long"#))

                .arg(clap::Arg::new(r#"paramFloat"#)
                   .help(r#"Float param {OPTIONAL,type:float,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('k'))

                .arg(clap::Arg::new(r#"paramDouble"#)
                   .help(r#"Double param {OPTIONAL,type:double,default:""}"#)
                   .takes_value(true)
                   .required(false)
                   .multiple_occurrences(false)
                   .short('l'))

        .arg(clap::Arg::new(r#"PARAMG"#)
           .help(r#"Positional integer param, positional param is always \"required\" {REQUIRED,type:uint64}"#)
           .required(true)
           .index(1)
           .multiple_occurrences(false))


        .arg(clap::Arg::new(r#"P-A-R-A-M-G-2"#)
           .help(r#"Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false {REQUIRED,type:bool}"#)
           .required(true)
           .index(2)
           .multiple_occurrences(false))


        .arg(clap::Arg::new(r#"PARAM-FLOAT"#)
           .help(r#"Positional float param {REQUIRED,type:float}"#)
           .required(true)
           .index(3)
           .multiple_occurrences(false))


        .arg(clap::Arg::new(r#"PARAM-DOUBLE"#)
           .help(r#"Positional double param {REQUIRED,type:double}"#)
           .required(true)
           .index(4)
           .multiple_occurrences(false))


        .arg(clap::Arg::new(r#"PARAMH"#)
           .help(r#"Positional repeating string params, there may be only one repeating positional param {REQUIRED,type:string}"#)
           .required(true)
           .index(5)
           .multiple_occurrences(true))

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

    let has_parama = matches.is_present("paramA");
    config.parama = matches.value_of("paramA").map(|o| o.parse::<String>().ok()).flatten();
    if has_parama && !config.has_parama() {
        let err = format!("Type 'String' conversion failed for 'paramA' with value '{}'", matches.value_of("paramA").unwrap());
        return Err(err);
    }

    let has_paramb = matches.is_present("paramB");
    config.paramb = matches.value_of("paramB").map(|o| o.parse::<u32>().ok()).flatten();
    if has_paramb && !config.has_paramb() {
        let err = format!("Type 'u32' conversion failed for 'paramB' with value '{}'", matches.value_of("paramB").unwrap());
        return Err(err);
    }

    let has_paramc = matches.is_present("paramC");
    config.paramc = matches.value_of("paramC").map(|o| o.parse::<i32>().ok()).flatten();
    if has_paramc && !config.has_paramc() {
        let err = format!("Type 'i32' conversion failed for 'paramC' with value '{}'", matches.value_of("paramC").unwrap());
        return Err(err);
    }

    let has_paramd = matches.is_present("paramD");
    config.paramd = matches.value_of("paramD").map(|o| o.parse::<f32>().ok()).flatten();
    if has_paramd && !config.has_paramd() {
        let err = format!("Type 'f32' conversion failed for 'paramD' with value '{}'", matches.value_of("paramD").unwrap());
        return Err(err);
    }

    let has_parame = matches.is_present("paramE");
    if !allow_incomplete && !has_parame {
        return Err("Required 'paramE' is missing".to_string());
    }
    config.parame = matches.value_of("paramE").map(|o| o.parse::<String>().ok()).flatten();
    if has_parame && !config.has_parame() {
        let err = format!("Type 'String' conversion failed for 'paramE' with value '{}'", matches.value_of("paramE").unwrap());
        return Err(err);
    }

    let count_paramf : usize = matches.occurrences_of("paramF").try_into().unwrap();
    config.paramf = matches.values_of("paramF")
        .map(|vals| vals.map(|o| o.parse::<i32>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_paramf != config.paramf.len() {
        return Err("Type 'i32' conversion failed for 'paramF'".to_string());
    }

    let has_paramg = matches.is_present("PARAMG");
    if !allow_incomplete && !has_paramg {
        return Err("Required 'PARAMG' is missing".to_string());
    }
    config.paramg = matches.value_of("PARAMG").map(|o| o.parse::<u64>().ok()).flatten();
    if has_paramg && !config.has_paramg() {
        let err = format!("Type 'u64' conversion failed for 'PARAMG' with value '{}'", matches.value_of("PARAMG").unwrap());
        return Err(err);
    }

    let has_p_a_r_a_m_g_2 = matches.is_present("P-A-R-A-M-G-2");
    if !allow_incomplete && !has_p_a_r_a_m_g_2 {
        return Err("Required 'P-A-R-A-M-G-2' is missing".to_string());
    }
    if has_p_a_r_a_m_g_2 && matches.value_of("P-A-R-A-M-G-2").is_none() {
        config.p_a_r_a_m_g_2 = Some(true);
    } else {
        config.p_a_r_a_m_g_2 = matches.value_of("P-A-R-A-M-G-2").map(|o| o.parse::<bool>().ok()).flatten();
        if has_p_a_r_a_m_g_2 && !config.has_p_a_r_a_m_g_2() {
            let err = format!("Type 'bool' conversion failed for 'P-A-R-A-M-G-2' with value '{}'", matches.value_of("P-A-R-A-M-G-2").unwrap());
            return Err(err);
        }
    }

    let has_param_i = matches.is_present("param-I");
    if has_param_i && matches.value_of("param-I").is_none() {
        config.param_i = Some(true);
    } else {
        config.param_i = matches.value_of("param-I").map(|o| o.parse::<bool>().ok()).flatten();
        if has_param_i && !config.has_param_i() {
            let err = format!("Type 'bool' conversion failed for 'param-I' with value '{}'", matches.value_of("param-I").unwrap());
            return Err(err);
        }
    }

    let has_param_j = matches.is_present("param-J");
    if has_param_j && matches.value_of("param-J").is_none() {
        config.param_j = Some(true);
    } else {
        config.param_j = matches.value_of("param-J").map(|o| o.parse::<bool>().ok()).flatten();
        if has_param_j && !config.has_param_j() {
            let err = format!("Type 'bool' conversion failed for 'param-J' with value '{}'", matches.value_of("param-J").unwrap());
            return Err(err);
        }
    }

    let has_param_float = matches.is_present("PARAM-FLOAT");
    config.param_float = matches.value_of("PARAM-FLOAT").map(|o| o.parse::<f32>().ok()).flatten();
    if has_param_float && !config.has_param_float() {
        let err = format!("Type 'f32' conversion failed for 'PARAM-FLOAT' with value '{}'", matches.value_of("PARAM-FLOAT").unwrap());
        return Err(err);
    }

    let has_param_double = matches.is_present("PARAM-DOUBLE");
    config.param_double = matches.value_of("PARAM-DOUBLE").map(|o| o.parse::<f64>().ok()).flatten();
    if has_param_double && !config.has_param_double() {
        let err = format!("Type 'f64' conversion failed for 'PARAM-DOUBLE' with value '{}'", matches.value_of("PARAM-DOUBLE").unwrap());
        return Err(err);
    }

    let count_paramh : usize = matches.occurrences_of("PARAMH").try_into().unwrap();
    if !allow_incomplete && count_paramh == 0 {
        return Err("Required at least one positional 'PARAMH'".to_string());
    }
    config.paramh = matches.values_of("PARAMH")
        .map(|vals| vals.map(|o| o.parse::<String>().ok().unwrap()).collect::<Vec<_>>())
        .unwrap_or_default();
    if count_paramh != config.paramh.len() {
        return Err("Type 'String' conversion failed for 'PARAMH'".to_string());
    }

    let has_paramfloat = matches.is_present("paramFloat");
    config.paramfloat = matches.value_of("paramFloat").map(|o| o.parse::<f32>().ok()).flatten();
    if has_paramfloat && !config.has_paramfloat() {
        let err = format!("Type 'f32' conversion failed for 'paramFloat' with value '{}'", matches.value_of("paramFloat").unwrap());
        return Err(err);
    }

    let has_paramdouble = matches.is_present("paramDouble");
    config.paramdouble = matches.value_of("paramDouble").map(|o| o.parse::<f64>().ok()).flatten();
    if has_paramdouble && !config.has_paramdouble() {
        let err = format!("Type 'f64' conversion failed for 'paramDouble' with value '{}'", matches.value_of("paramDouble").unwrap());
        return Err(err);
    }


    Ok(config)
}

}