#!/bin/bash

# Options preparation
function multy_command_copy_prepareOptions()
{
    # Common Variables
    PROTOARGS_USAGE=""

    # Print help and exit
    multy_command_copy_help=false
    multy_command_copy_help_PRESENT=false

    # Recursive copy
    multy_command_copy_recursive=false
    multy_command_copy_recursive_PRESENT=false

    # Path to source path
    multy_command_copy_SRC=""
    multy_command_copy_SRC_PRESENT=false

    # Path to destination path
    multy_command_copy_DST=""
    multy_command_copy_DST_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function multy_command_copy_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    multy_command_copy_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] [-r] SRC DST

${description}

positional arguments:
  SRC              Path to source path {REQUIRED,type:string}
  DST              Path to destination path {REQUIRED,type:string}

optional arguments:
  -h, --help       show this help message and exit
  -r, --recursive  Recursive copy {OPTIONAL,type:bool,default:"false"}

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
function multy_command_copy_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    multy_command_copy_prepareOptions


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            -h|--help)
                multy_command_copy_help=true
                multy_command_copy_help_PRESENT=true
                shift
                ;;

            -r|--recursive)
                multy_command_copy_recursive=true
                multy_command_copy_recursive_PRESENT=true
                shift
                ;;

            -*|--*)
                echo "Unknown option '$1'"
                multy_command_copy_usage
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

