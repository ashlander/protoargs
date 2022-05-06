//use crate::simple_pa;
//#[path = "simple_pa.rs"] mod simple_pa;

#[cfg(test)]
mod simple_tests {

    // Note this useful idiom: importing names from outer (for mod tests) scope.
    //use super::*;

    #[test]
    fn simple_usage() {
        let description = "Desription";
        let argv = vec!["program", "--help"];

        // check usage
        let usage = crate::simple_pa::simple_pa::usage(argv[0], description);
        assert_eq!(usage.trim().is_empty(), false);
    }

    #[test]
    fn check_all_positive() {
        let description = "Desription";
        let argv = vec![ "program"
           , "--count", "1"
           , "--configuration", "/tmp/conf"
           , "--flags", "true"
           , "--flags", "false"
           , "-c", "flags should be true and false"
           , "--o-underscore", "no underscore"
           , "--r-underscore", "no underscore"
           , "--a-underscore", "no underscore0"
           , "--a-underscore", "no underscore1"
        ];

        let rconfig = crate::simple_pa::simple_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
        let config = rconfig.ok().unwrap();

        assert_eq!( 1, config.count() );

        assert_eq!( "/tmp/conf", config.configuration() );

        assert_eq!( 2, config.flags().len() );
        assert_eq!( true, config.get_flags(0) );
        assert_eq!( false, config.get_flags(1) );

        assert_eq!( "flags should be true and false", config.c() );

        assert_eq!( "no underscore", config.r_underscore() );
        assert_eq!( "no underscore", config.o_underscore() );

        assert_eq!( 2, config.a_underscore().len() );
        assert_eq!( "no underscore0", config.get_a_underscore(0) );
        assert_eq!( "no underscore1", config.get_a_underscore(1) );
    }

    // trailing positional will be skipped
    #[test]
    //#[ignore] // FIXME clap fails on trailing positionals if they are not covered with config and
    // FIXME do not continue other tests
    fn check_no_positional() {
        let description = "Desription";
        let argv = vec![ "program"
           , "--count", "1"
           , "--configuration", "/tmp/conf"
           , "--flags", "true"
           , "--flags", "false"
           , "-c", "flags should be true and false"
           , "--r-underscore", "no underscore"
           , "positional_value"
           , "positional_value"
           , "positional_value"
           , "positional_value"
           , "positional_value"
        ];

        let rconfig = crate::simple_pa::simple_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
        let config = rconfig.ok().unwrap();

        assert_eq!( 1, config.count() );

        assert_eq!( "/tmp/conf", config.configuration() );

        assert_eq!( 2, config.flags().len() );
        assert_eq!( true, config.get_flags(0) );
        assert_eq!( false, config.get_flags(1) );

        assert_eq!( "flags should be true and false", config.c() );
    }


    #[test]
    fn check_wrong_type() {
        let description = "Desription";
        let argv = vec![ "program"
           , "--count", "stringnotdigit"
           , "--configuration", "/tmp/conf"
           , "--flags", "true"
           , "--flags", "false"
           , "-c", "flags should be true and false"
           , "--r-underscore", "no underscore"
        ];

        let rconfig = crate::simple_pa::simple_pa::parse_debug(argv[0], &argv[..], description);
        assert_eq!( true, rconfig.is_err() );
    }
}
