#!/bin/bash

# Options preparation
function bools_prepareOptions()
{
    # Common Variables
    bools_PROTOARGS_USAGE=""

    # Required bool
    bools_req_bool=false
    bools_req_bool_PRESENT=false

    # Optional bool
    bools_opt_bool=true
    bools_opt_bool_PRESENT=false

    # Repeated bool
    bools_rep_bool=()
    bools_rep_bool_PRESENT=false
    bools_rep_bool_COUNT=0

    # Positional bool param
    bools_OPTBOOL=false
    bools_OPTBOOL_PRESENT=false

    # Positional bool param
    bools_ALTBOOL=false
    bools_ALTBOOL_PRESENT=false

    # Positional repeating bool params, there may be only one repeating positional param at the end of positional block
    bools_REOBOOL=()
    bools_REOBOOL_PRESENT=false
    bools_REOBOOL_COUNT=0

    # Print help and exit, check non-positional accepted after positional
    bools_printHelp=false
    bools_printHelp_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function bools_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    bools_PROTOARGS_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] --rb [--optbool] [--repbool [rep_bool ...]]
                  OPTBOOL ALTBOOL REOBOOL [REOBOOL ...]

${description}

positional arguments:
  OPTBOOL               Positional bool param {REQUIRED,type:bool}
  ALTBOOL               Positional bool param {REQUIRED,type:bool}
  REOBOOL               Positional repeating bool params, there may be only
                        one repeating positional param at the end of
                        positional block {REQUIRED,type:bool}

optional arguments:
  -h, --help            show this help message and exit
  --rb, --reqbool       Required bool {REQUIRED,type:bool,default:""}
  --optbool             Optional bool {OPTIONAL,type:bool,default:"true"}
  --repbool [rep_bool ...]
                        Repeated bool {REPEATED,type:bool,default:""}

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
function bools_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    bools_prepareOptions
    bools_usage "${program}" "${description}"


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            --rb|--reqbool)
                bools_req_bool=true
                bools_req_bool_PRESENT=true
                shift
                ;;

            --optbool)
                bools_opt_bool=true
                bools_opt_bool_PRESENT=true
                shift
                ;;

            --repbool)
                local value=$2
                if [ "${value}" != true ] && [ "${value}" != false ]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'rep-bool' of type bool but the value is '${value}'"
                        echo "${bools_PROTOARGS_USAGE}"
                        return 1
                    fi
                else
                    bools_rep_bool+=("$2")
                fi
                bools_rep_bool_PRESENT=true
                bools_rep_bool_COUNT=$((bools_rep_bool_COUNT + 1))
                shift # past argument
                shift # past value
                ;;

            --repbool=*)
                local value="${1#*=}"
                if [ "${value}" != true ] && [ "${value}" != false ]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'rep-bool' of type bool but the value is '${value}'"
                        echo "${bools_PROTOARGS_USAGE}"
                        return 1
                    fi
                else
                    bools_rep_bool+=("${1#*=}")
                fi
                bools_rep_bool_PRESENT=true
                bools_rep_bool_COUNT=$((bools_rep_bool_COUNT + 1))
                shift # past argument=value
                ;;

            --help)
                bools_printHelp=true
                bools_printHelp_PRESENT=true
                shift
                ;;

            -*|--*)
                if ! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]] || ! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
                    echo "[ERR] Unknown option '$1'"
                    echo "${bools_PROTOARGS_USAGE}"
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
        echo "[ERR] Positional 'OPTBOOL' parameter is not set"
        echo "${bools_PROTOARGS_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[0]}"
    if [ "${value}" != true ] && [ "${value}" != false ]; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional 'OPTBOOL' parameter expected to be of type 'bool' but value is '$value'"
            echo "${bools_PROTOARGS_USAGE}"
            return 1
        fi
    else
        bools_OPTBOOL="${POSITIONAL_ARGS[0]}"
        bools_OPTBOOL_PRESENT=true
    fi

    if [ "$allow_incomplete" == false ] && [ 1 -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "[ERR] Positional 'ALTBOOL' parameter is not set"
        echo "${bools_PROTOARGS_USAGE}"
        return 1
    fi
    local value="${POSITIONAL_ARGS[1]}"
    if [ "${value}" != true ] && [ "${value}" != false ]; then
        if [ "$allow_incomplete" == false ]; then
            echo "[ERR] Positional 'ALTBOOL' parameter expected to be of type 'bool' but value is '$value'"
            echo "${bools_PROTOARGS_USAGE}"
            return 1
        fi
    else
        bools_ALTBOOL="${POSITIONAL_ARGS[1]}"
        bools_ALTBOOL_PRESENT=true
    fi

    if [ "$allow_incomplete" == false ] && [ 2 -ge ${#POSITIONAL_ARGS[@]} ]; then
        echo "[ERR] Positional 'REOBOOL' parameter is not set, needs to be at least 1"
        echo "${bools_PROTOARGS_USAGE}"
        return 1
    fi
    local expected=$((${#POSITIONAL_ARGS[@]} - 2))
    local position=2
    local processed=0
    while [[ "$bools_REOBOOL_COUNT" -lt "$expected" ]] && [[ "$processed" -lt "$expected" ]]; do
        local value="${POSITIONAL_ARGS[$position]}"
        if [ "${value}" != true ] && [ "${value}" != false ]; then
            if [ "$allow_incomplete" == false ]; then
                echo "[ERR] Positional 'REOBOOL' parameter expected to be of type 'bool' but value is '$value'"
                echo "${bools_PROTOARGS_USAGE}"
                return 1
            fi
        else
            bools_REOBOOL+=("${POSITIONAL_ARGS[$position]}")
            bools_REOBOOL_COUNT=$(($bools_REOBOOL_COUNT + 1))
        fi
        position=$((position + 1))
        processed=$((processed + 1))
    done
    if [ "$bools_REOBOOL_COUNT" -gt 0 ]; then
        bools_REOBOOL_PRESENT=true
    fi


    if [ "$allow_incomplete" == false ] && [ $bools_req_bool_PRESENT == false ]; then
        echo "[ERR] Required 'req-bool' is missing"
        echo "${bools_PROTOARGS_USAGE}"
        return 1
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
# returns `bools_PROTOARGS_ARGS` Resulting set of args
function bools_remove_args_tail() #(keep, args)
{
    bools_PROTOARGS_ARGS=()
    local keep=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$keep" ]]; do
        bools_PROTOARGS_ARGS+=("$1")
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
# returns `bools_PROTOARGS_ARGS` Resulting set of args
function bools_keep_args_tail()
{
    local erase=$1
    shift # past number
    local pos=0
    while [[ "$pos" -lt "$erase" ]]; do
        shift
        pos=$((pos + 1))
    done
    bools_PROTOARGS_ARGS=("$@")
}


