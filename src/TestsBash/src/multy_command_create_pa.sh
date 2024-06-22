#!/bin/bash

# Options preparation
function multy_command_create_prepareOptions()
{
    # Common Variables
    multy_command_create_PROTOARG_USAGE=""

    # Print help and exit
    multy_command_create_help=false
    multy_command_create_help_PRESENT=false

    # Size of the file
    multy_command_create_size=0
    multy_command_create_size_PRESENT=false

    # Path to file to create
    multy_command_create_PATH=""
    multy_command_create_PATH_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function multy_command_create_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    multy_command_create_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] [-s size] PATH

${description}

positional arguments:
  PATH                  Path to file to create {REQUIRED,type:string}

optional arguments:
  -h, --help            show this help message and exit
  -s size, --size size  Size of the file {OPTIONAL,type:uint64,default:"0"}

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
function multy_command_create_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    multy_command_create_prepareOptions
    multy_command_create_usage "${program}" "${description}"


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            -h|--help)
                multy_command_create_help=true
                multy_command_create_help_PRESENT=true
                shift
                ;;

            -s|--size)
                local value=$2
                if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'size' of type uint64 but the value is '${value}'"
                        echo "${multy_command_create_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    multy_command_create_size=$2
                fi
                multy_command_create_size_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -s=*|--size=*)
                local value="${1#*=}"
                if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'size' of type uint64 but the value is '${value}'"
                        echo "${multy_command_create_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    multy_command_create_size="${1#*=}"
                fi
                multy_command_create_size_PRESENT=true
                shift # past argument=value
                ;;

            -*|--*)
                if ! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]] || ! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
                    echo "[ERR] Unknown option '$1'"
                    echo "${multy_command_create_PROTOARG_USAGE}"
                    return 1
                fi
                POSITIONAL_ARGS+=("$1") # save positional numeric arg
                shift # past argument
                ;;
            *)
                POSITIONAL_ARGS+=("$1") # save positional arg
                shift # past argument
                ;;
        esac
    done

    set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters


    if [ "$allow_incomplete" == false ] && [ 0 -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "[ERR] Positional 'PATH' parameter is not set"
        echo "${multy_command_create_PROTOARG_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[0]}"
    if [ -z "0" ]; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional 'PATH' parameter expected to be of type 'string' but value is '$value'"
            echo "${multy_command_create_PROTOARG_USAGE}"
            return 1
        fi
    else
        multy_command_create_PATH="${POSITIONAL_ARGS[0]}"
        multy_command_create_PATH_PRESENT=true
    fi

    return 0
}

