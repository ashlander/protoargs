#!/bin/bash

# Options preparation
function simple_prepareOptions()
{
    # Common Variables
    simple_PROTOARG_USAGE=""

    # Converted to --count
    simple_count=1
    simple_count_PRESENT=false

    # Converted to --configuration
    simple_configuration=""
    simple_configuration_PRESENT=false

    # Converted to --flags, each encounter will be stored in list
    simple_flags=()
    simple_flags_PRESENT=false
    simple_flags_COUNT=0

    # Converted to --version
    simple_version=false
    simple_version_PRESENT=false

    # Converted to --help
    simple_help=false
    simple_help_PRESENT=false

    # Converted to -c short option
    simple_c="some value"
    simple_c_PRESENT=false

    # Converted to r-underscore long option
    simple_r_underscore=""
    simple_r_underscore_PRESENT=false

    # Converted to o-underscore long option
    simple_o_underscore=""
    simple_o_underscore_PRESENT=false

    # Converted to a-underscore long option
    simple_a_underscore=()
    simple_a_underscore_PRESENT=false
    simple_a_underscore_COUNT=0

    # Converted to s-quote-in-descr long option, "checking quotes"
    simple_s_quote_in_descr=""
    simple_s_quote_in_descr_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function simple_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    simple_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] --count count [--configuration configuration]
                  [--flags [flags]] [--version] [-c c] --r-underscore
                  r_underscore [--o-underscore o_underscore]
                  [--a-underscore [a_underscore]]
                  [--s-quote-in-descr s_quote_in_descr]

${description}

optional arguments:
  -h, --help            show this help message and exit
  --count count         Converted to --count
                        {REQUIRED,type:uint64,default:"1"}
  --configuration configuration
                        Converted to --configuration
                        {OPTIONAL,type:string,default:""}
  --flags [flags]       Converted to --flags, each encounter will be stored in
                        list {REPEATED,type:bool,default:""}
  --version             Converted to --version
                        {OPTIONAL,type:bool,default:"false"}
  -c c                  Converted to -c short option
                        {OPTIONAL,type:string,default:"some value"}
  --r-underscore r_underscore
                        Converted to r-underscore long option
                        {REQUIRED,type:string,default:""}
  --o-underscore o_underscore
                        Converted to o-underscore long option
                        {OPTIONAL,type:string,default:""}
  --a-underscore [a_underscore]
                        Converted to a-underscore long option
                        {REPEATED,type:string,default:""}
  --s-quote-in-descr s_quote_in_descr
                        Converted to s-quote-in-descr long option, "checking
                        quotes" {OPTIONAL,type:string,default:""}

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
function simple_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    simple_prepareOptions
    simple_usage "${program}" "${description}"


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            --count)
                local value=$2
                if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'count' of type uint64 but the value is '${value}'"
                        echo "${simple_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    simple_count=$2
                fi
                simple_count_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --count=*)
                local value="${1#*=}"
                if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'count' of type uint64 but the value is '${value}'"
                        echo "${simple_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    simple_count="${1#*=}"
                fi
                simple_count_PRESENT=true
                shift # past argument=value
                ;;

            --configuration)
                simple_configuration="$2"
                simple_configuration_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --configuration=*)
                simple_configuration="${1#*=}"
                simple_configuration_PRESENT=true
                shift # past argument=value
                ;;

            --flags=*)
                local value="${1#*=}"
                if [ "${value}" != true ] && [ "${value}" != false ]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'flags' of type bool but the value is '${value}'"
                        echo "${simple_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    simple_flags+=("${1#*=}")
                fi
                simple_flags_PRESENT=true
                simple_flags_COUNT=$((simple_flags_COUNT + 1))
                shift # past argument=value
                ;;

            --version)
                simple_version=true
                simple_version_PRESENT=true
                shift
                ;;

            --help)
                simple_help=true
                simple_help_PRESENT=true
                shift
                ;;

            -c)
                simple_c="$2"
                simple_c_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -c=*)
                simple_c="${1#*=}"
                simple_c_PRESENT=true
                shift # past argument=value
                ;;

            --r-underscore)
                simple_r_underscore="$2"
                simple_r_underscore_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --r-underscore=*)
                simple_r_underscore="${1#*=}"
                simple_r_underscore_PRESENT=true
                shift # past argument=value
                ;;

            --o-underscore)
                simple_o_underscore="$2"
                simple_o_underscore_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --o-underscore=*)
                simple_o_underscore="${1#*=}"
                simple_o_underscore_PRESENT=true
                shift # past argument=value
                ;;

            --a-underscore)
                local value=$2
                if [ -z "0" ]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'a-underscore' of type string but the value is '${value}'"
                        echo "${simple_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    simple_a_underscore+=("$2")
                fi
                simple_a_underscore_PRESENT=true
                simple_a_underscore_COUNT=$((simple_a_underscore_COUNT + 1))
                shift # past argument
                shift # past value
                ;;

            --a-underscore=*)
                local value="${1#*=}"
                if [ -z "0" ]; then
                    if [ "$allow_incomplete" == false ]; then
                        echo "[ERR] expected 'a-underscore' of type string but the value is '${value}'"
                        echo "${simple_PROTOARG_USAGE}"
                        return 1
                    fi
                else
                    simple_a_underscore+=("${1#*=}")
                fi
                simple_a_underscore_PRESENT=true
                simple_a_underscore_COUNT=$((simple_a_underscore_COUNT + 1))
                shift # past argument=value
                ;;

            --s-quote-in-descr)
                simple_s_quote_in_descr="$2"
                simple_s_quote_in_descr_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --s-quote-in-descr=*)
                simple_s_quote_in_descr="${1#*=}"
                simple_s_quote_in_descr_PRESENT=true
                shift # past argument=value
                ;;

            -*|--*)
                if ! [[ "${value}" =~ ^[+-]?[0-9]+([.][0-9]+)?$ ]] || ! [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
                    echo "[ERR] Unknown option '$1'"
                    echo "${simple_PROTOARG_USAGE}"
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


    if [ "$allow_incomplete" == false ] && [ $simple_count_PRESENT == false ]; then
        echo "[ERR] Required 'count' is missing"
        echo "${simple_PROTOARG_USAGE}"
        return 1
    fi

    if [ "$allow_incomplete" == false ] && [ $simple_r_underscore_PRESENT == false ]; then
        echo "[ERR] Required 'r-underscore' is missing"
        echo "${simple_PROTOARG_USAGE}"
        return 1
    fi

    return 0
}

