#!/bin/bash

# Options preparation
function multy_command_prepareOptions()
{
    # Common Variables
    PROTOARGS_USAGE=""

    # Print help and exit
    multy_command_help=false
    multy_command_help_PRESENT=false

    # Command (create, copy)
    multy_command_COMMAND=""
    multy_command_COMMAND_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function multy_command_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    multy_command_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] COMMAND

${description}

positional arguments:
  COMMAND     Command (create, copy) {REQUIRED,type:string}

optional arguments:
  -h, --help  show this help message and exit

PROTOARGS_EOM
)"
}


# Parse command line arguments, and return filled configuration
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
# * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
# wrong type cast will produce error anyway
# * `args` - Command line arguments, use $@ to pass them
#
# returns Result with configuration structure, or error message
function multy_command_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    multy_command_prepareOptions


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            -h|--help)
                multy_command_help=true
                multy_command_help_PRESENT=true
                shift
                ;;

            -*|--*)
                echo "Unknown option '$1'"
                multy_command_usage
                echo "${PROTOARGS_USAGE}"
                return 1
                ;;
            *)
                POSITIONAL_ARGS+=("$1") # save positional arg
                shift # past argument
                ;;
            esac
        done

        set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters



    return 0
}
