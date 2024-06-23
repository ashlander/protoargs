#!/bin/bash

# Options preparation
function multy_command_copy_prepareOptions()
{
    # Common Variables
    multy_command_copy_PROTOARGS_USAGE=""

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

    multy_command_copy_PROTOARGS_USAGE="$(cat << PROTOARGS_EOM
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
    multy_command_copy_usage "${program}" "${description}"


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
                if ! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]] || ! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
                    echo "[ERR] Unknown option '$1'"
                    echo "${multy_command_copy_PROTOARGS_USAGE}"
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
        echo "[ERR] Positional 'SRC' parameter is not set"
        echo "${multy_command_copy_PROTOARGS_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[0]}"
    if [ -z "0" ]; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional 'SRC' parameter expected to be of type 'string' but value is '$value'"
            echo "${multy_command_copy_PROTOARGS_USAGE}"
            return 1
        fi
    else
        multy_command_copy_SRC="${POSITIONAL_ARGS[0]}"
        multy_command_copy_SRC_PRESENT=true
    fi

    if [ "$allow_incomplete" == false ] && [ 1 -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "[ERR] Positional 'DST' parameter is not set"
        echo "${multy_command_copy_PROTOARGS_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[1]}"
    if [ -z "0" ]; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional 'DST' parameter expected to be of type 'string' but value is '$value'"
            echo "${multy_command_copy_PROTOARGS_USAGE}"
            return 1
        fi
    else
        multy_command_copy_DST="${POSITIONAL_ARGS[1]}"
        multy_command_copy_DST_PRESENT=true
    fi

    return 0
}

########################################################################
# Helpers
########################################################################

# Keep some number of first arguments, remove the rest
#
# Arguments:
#
# * `keep` - Number of arguments to keep
# * `args` - Command line arguments, list, use $@ to pass them
#
# returns `multy_command_copy_PROTOARGS_ARGS` Resulting set of args
function multy_command_copy_remove_args_tail() #(keep, args)
{
    multy_command_copy_PROTOARGS_ARGS=()
    local keep=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$keep" ]]; do
        multy_command_copy_PROTOARGS_ARGS+=("$1")
        shift
        pos=$((pos + 1))
    done
}

# Remove some number of first arguments, keep the rest
#
# Arguments:
#
# * `erase` - Number of arguments to remove
# * `args` - Command line arguments, list, use $@ to pass them
#
# returns `multy_command_copy_PROTOARGS_ARGS` Resulting set of args
function multy_command_copy_keep_args_tail()
{
    local erase=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$erase" ]]; do
        shift
        pos=$((pos + 1))
    done
    multy_command_copy_PROTOARGS_ARGS=("$@")
}


