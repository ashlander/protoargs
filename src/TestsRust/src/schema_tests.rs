//use crate::simple_pa;
//#[path = "simple_pa.rs"] mod simple_pa;

#[cfg(test)]
mod schema_tests {

    // Note this useful idiom: importing names from outer (for mod tests) scope.
    //use super::*;

    #[test]
    fn schema_usage() {
        let description = "Desription";
        let argv = vec!["program", "--help"];

        // check usage
        let usage = crate::schema_pa::schema_pa::usage(argv[0], description);
        assert_eq!(usage.trim().is_empty(), false);

        // check configuration
        let rconfig = crate::schema_pa::schema_pa::parse_ext(argv[0], &argv[..], description, true);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
    }

    #[test]
    fn connect_short_and_long_args_together() {
        let description = "Desription";
        let argv = vec![ "program"
           , "-e", "valueE"
           , "--a-long-param", "somevalue" // inside only '-a' is analized
           , "50" // paramG
           , "true" // bool P-A-R-A-M-G-2
           , "0.5" // PARAM-FLOAT
           , "0.7" // PARAM-DOUBLE
           , "pos1", "pos2", "pos3"
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
        let config = rconfig.ok().unwrap();

        assert!( config.has_parama() );
    }

    #[test]
    fn schema_positive_short() {
        let description = "Desription";
        let argv = vec![ "program"
           ,"-e", "valueE"
           , "50" // paramG
           , "false" // bool paramG
           , "0.5" // PARAM-FLOAT
           , "0.7" // PARAM-DOUBLE
           , "pos1", "pos2", "pos3"
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
        let config = rconfig.ok().unwrap();

        // check defaults
        assert_eq!( false, config.has_parama() );
        assert_eq!( "// tricky default value", config.parama() );

        assert_eq!( false, config.has_paramb() );
        assert_eq!( 10, config.paramb() );

        assert_eq!( false, config.has_paramc() );
        assert_eq!( 0, config.paramc() );

        assert_eq!( false, config.has_paramd() );
        assert_eq!( 0.0, config.paramd() );

        assert_eq!( "valueE", config.parame() );

        assert_eq!( 0, config.paramf().len() );

        assert_eq!( false, config.has_param_i() );
        assert_eq!( true, config.param_i() );

        assert_eq!( false, config.has_param_j() );
        assert_eq!( false, config.param_j() );
    }

    #[test]
    fn schema_positive_all() {
        let description = "Desription";
        let argv = vec![ "program"
           ,"-e", "valueE"
           ,"--a-long-param", "somevalue"
           ,"--b-long-param", "4"
           ,"-c", "555"
           ,"--d-long-param", "555.5"
           ,"-f", "1"
           ,"-f", "2"
           ,"-f", "3"
           ,"-i"
           ,"--j-long"
           , "50" // paramG
           , "false" // bool paramG
           , "0.5" // PARAM-FLOAT
           , "0.7" // PARAM-DOUBLE
           , "pos1", "pos2", "pos3" // paramH
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
        let config = rconfig.ok().unwrap();

        assert_eq!( true, config.has_parama() );
        assert_eq!( "somevalue", config.parama() );

        assert_eq!( true, config.has_paramb() );
        assert_eq!( 4, config.paramb() );

        assert_eq!( true, config.has_paramc() );
        assert_eq!( 555, config.paramc() );

        assert_eq!( true, config.has_paramd() );
        assert_eq!( 555.5, config.paramd() );

        assert_eq!( "valueE", config.parame() );

        assert_eq!( 3, config.paramf().len() );

        assert_eq!( true, config.has_param_i() );
        assert_eq!( true, config.param_i() );

        assert_eq!( true, config.has_param_j() );
        assert_eq!( true, config.param_j() );
    }

    #[test]
    //#[ignore] // FIXME Negative tests breaks execution
    fn missing_required() {
        let description = "Desription";
        let argv = vec![ "program"
           , "50" // paramG
           , "0" // bool paramG
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( false, rconfig.is_ok() );
    }

    #[test]
    //#[ignore] // FIXME Negative tests breaks execution
    fn missing_repeated_positional() {
        let description = "Desription";
        let argv = vec![ "program"
           ,"-e", "valueE"
           , "50" // paramG
           , "true" // bool paramG
           , "0.5" // PARAM-FLOAT
           , "0.7" // PARAM-DOUBLE
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( false, rconfig.is_ok() );
    }

    #[test]
    fn positional_wrong_type() {
        let description = "Desription";
        let argv = vec![ "program"
           ,"-e", "valueE"
           , "50f" // paramG
           , "0e" // bool paramG
           , "0.5d" // PARAM-FLOAT
           , "0.7d" // PARAM-DOUBLE
           , "pos1", "pos2", "pos3"
        ];

        let rconfig = crate::schema_pa::schema_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( false, rconfig.is_ok() );
    }

}
