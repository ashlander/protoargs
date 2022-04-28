//use crate::simple_pa;
//#[path = "simple_pa.rs"] mod simple_pa;

#[cfg(test)]
mod multy_tests {

    // Note this useful idiom: importing names from outer (for mod tests) scope.
    //use super::*;

    #[test]
    fn multi_commands_usage() {
        let description = "Desription";
        let argv = vec![ "program"
           , "-e", "valueE"
           ,"-h"
        ];

        // check usage
        let usage = crate::multy_command_pa::multy_command_pa::usage(argv[0], description);
        assert_eq!(usage.trim().is_empty(), false);

        // check configuration
        let rconfig = crate::multy_command_pa::multy_command_pa::parse_ext(argv[0], &argv[..], description, true);
        assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
    }

   #[test]
    fn multi_commands_create_usage() {
        let description = "Desription";
        let argv = vec![ "program"
           , "create"
           ,"-h"
        ];

        let mut program = argv[0].to_string();
        let command: String;

        { // check main args
            let rconfig = crate::multy_command_pa::multy_command_pa::parse_str(&program[..], &argv[..2], description);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!("create", config.command());
            command = config.command();
        }

        { // check create args
            program.push_str(" ");
            program.push_str(&command);
            let mut argv_nocmd = argv.clone();
            argv_nocmd.remove(1); // remove command name

            let rconfig = crate::multy_command_create_pa::multy_command_create_pa::parse_ext(&program[..], &argv_nocmd[..], description, true);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );

            let usage = crate::multy_command_create_pa::multy_command_create_pa::usage(&program[..], description);
            assert_eq!( false, usage.is_empty() );
        }
    }

    #[test]
    fn check_all_positive_create() {
        let description = "Desription";
        let argv = vec![ "program"
           , "create"
          ,"-s", "2048"
          , "/tmp/tmp.file"
        ];

        let mut program = argv[0].to_string();
        let command: String;

        { // check main args
            let rconfig = crate::multy_command_pa::multy_command_pa::parse_str(&program[..], &argv[..2], description);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!("create", config.command());
            command = config.command();
        }

        { // check create args
            program.push_str(" ");
            program.push_str(&command);
            let mut argv_nocmd = argv.clone();
            argv_nocmd.remove(1); // remove command name

            let rconfig = crate::multy_command_create_pa::multy_command_create_pa::parse_ext(&program[..], &argv_nocmd[..], description, true);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!(2048, config.size());
            assert_eq!("/tmp/tmp.file", config.path());
        }
    }

    #[test]
    fn multi_commands_copy_usage() {
        let description = "Desription";
        let argv = vec![ "program"
           , "copy"
           ,"-h"
        ];

        let mut program = argv[0].to_string();
        let command: String;

        { // check main args
            let rconfig = crate::multy_command_pa::multy_command_pa::parse_str(&program[..], &argv[..2], description);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!("copy", config.command());
            command = config.command();
        }

        { // check create args
            program.push_str(" ");
            program.push_str(&command);
            let mut argv_nocmd = argv.clone();
            argv_nocmd.remove(1); // remove command name

            let rconfig = crate::multy_command_copy_pa::multy_command_copy_pa::parse_ext(&program[..], &argv_nocmd[..], description, true);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );

            let usage = crate::multy_command_copy_pa::multy_command_copy_pa::usage(&program[..], description);
            assert_eq!( false, usage.is_empty() );
        }
    }

    #[test]
    fn check_all_positive_copy() {
        let description = "Desription";
        let argv = vec![ "program"
           , "copy"
           ,"-r"
           , "/tmp/tmp.file.src"
           , "/tmp/tmp.file.dst"
        ];

        let mut program = argv[0].to_string();
        let command: String;

        { // check main args
            let rconfig = crate::multy_command_pa::multy_command_pa::parse_str(&program[..], &argv[..2], description);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!("copy", config.command());
            command = config.command();
        }

        { // check create args
            program.push_str(" ");
            program.push_str(&command);
            let mut argv_nocmd = argv.clone();
            argv_nocmd.remove(1); // remove command name

            let rconfig = crate::multy_command_copy_pa::multy_command_copy_pa::parse_ext(&program[..], &argv_nocmd[..], description, true);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );

            let usage = crate::multy_command_copy_pa::multy_command_copy_pa::usage(&program[..], description);
            assert_eq!( false, usage.is_empty() );
            let config = rconfig.ok().unwrap();

            assert_eq!(true, config.recursive());
            assert_eq!("/tmp/tmp.file.src", config.src());
            assert_eq!("/tmp/tmp.file.dst", config.dst());
        }
    }

    #[test]
    fn check_subcommand_all_positive_copy() {
        let description = "Desription";
        let argv = vec![ "program"
           , "unused" // main command now should not have command field for this method
           , "copy"
           ,"-r"
           , "/tmp/tmp.file.src"
           , "/tmp/tmp.file.dst"
        ];

        // prepare command with subcommands
        let create_command = crate::multy_command_create_pa::multy_command_create_pa::prepare_options("create", description);
        let copy_command = crate::multy_command_copy_pa::multy_command_copy_pa::prepare_options("copy", description);
        let command = crate::multy_command_pa::multy_command_pa::prepare_options(argv[0], description)
            .subcommand(create_command)
            .subcommand(copy_command);

        // do parsing
        let matches = command.get_matches_from(&argv[..]);

        { // process values and generate general command config (without subcommands)
            let rconfig = crate::multy_command_pa::multy_command_pa::parse_matches(&matches, false);
            assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
            let config = rconfig.ok().unwrap();

            assert_eq!("unused", config.command());
        }

        {// process subcommands
            if let Some(matches) = matches.subcommand_matches("copy") {
                // process values and generate copy subcommand config
                let rconfig = crate::multy_command_copy_pa::multy_command_copy_pa::parse_matches(&matches, false);
                assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
                let config = rconfig.ok().unwrap();

                assert_eq!(true, config.recursive());
                assert_eq!("/tmp/tmp.file.src", config.src());
                assert_eq!("/tmp/tmp.file.dst", config.dst());
            } else if let Some(matches) = matches.subcommand_matches("create") {
                // process values and generate copy subcommand config
                let rconfig = crate::multy_command_create_pa::multy_command_create_pa::parse_matches(&matches, false);
                assert_eq!( true, rconfig.is_ok(), "{}", rconfig.err().unwrap() );
                let config = rconfig.ok().unwrap();

                assert_eq!(2048, config.size());
                assert_eq!("/tmp/tmp.file", config.path());
            }
        }
    }

}
