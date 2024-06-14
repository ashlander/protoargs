#!/bin/bash

# Options preparation
function schema_prepareOptions()
{
    # Common Variables
    PROTOARGS_USAGE=""

    # String param option with default value. Note: this comment will be taken as description
    schema_paramA="// tricky default value"
    schema_paramA_PRESENT=false

    # Integer param with default value
    schema_paramB=10
    schema_paramB_PRESENT=false

    # Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway
    schema_paramC=0
    schema_paramC_PRESENT=false

    # Float param without default value
    schema_paramD=0
    schema_paramD_PRESENT=false

    # String param which should be anyway
    schema_paramE=""
    schema_paramE_PRESENT=false

    # Integer param which may encounter multiple times
    schema_paramF=()
    schema_paramF_PRESENT=false
    schema_paramF_COUNT=0

    # Positional integer param, positional param is always \"required\"
    schema_PARAMG=0
    schema_PARAMG_PRESENT=false

    # Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false
    schema_P_A_R_A_M_G_2=false
    schema_P_A_R_A_M_G_2_PRESENT=false

    # Boolean arg with default value (despite it is declared after positional args, that is not a problem)
    schema_param_I=true
    schema_param_I_PRESENT=false

    # Boolean arg without default value
    schema_param_J=false
    schema_param_J_PRESENT=false

    # Positional float param
    schema_PARAM_FLOAT=0
    schema_PARAM_FLOAT_PRESENT=false

    # Positional double param
    schema_PARAM_DOUBLE=0
    schema_PARAM_DOUBLE_PRESENT=false

    # Positional repeating string params, there may be only one repeating positional param
    schema_PARAMH=()
    schema_PARAMH_PRESENT=false
    schema_PARAMH_COUNT=0

    # Print help and exit
    schema_printHelp=false
    schema_printHelp_PRESENT=false

    # Float param
    schema_paramFloat=0
    schema_paramFloat_PRESENT=false

    # Double param
    schema_paramDouble=0
    schema_paramDouble_PRESENT=false


}

# Get usage string
#
# Arguments:
#
# * `program` - Program name to display in help message
# * `description` - Description to display in help message
#
# returns String with usage information
function schema_usage() #(program, description)
{
    local program="$1"
    local description=$(echo "$2" | fold -w 80)

    schema_PROTOARG_USAGE="$(cat << PROTOARGS_EOM
usage: ${program} [-h] [-a paramA] [--b-long-param paramB] [-c paramC]
                  [--d-long-param paramD] -e paramE [-f paramF [paramF ...]]
                  [-i] [--j-long] [-k paramFloat] [-l paramDouble]
                  PARAMG P_A_R_A_M_G_2 PARAM_FLOAT PARAM_DOUBLE PARAMH
                  [PARAMH ...]

${description}

positional arguments:
  PARAMG                Positional integer param, positional param is always
                        \"required\" {REQUIRED,type:uint64}
  P_A_R_A_M_G_2         Positional boolean param, positional param is always
                        \"required\", Note: param set - true, missing - false
                        {REQUIRED,type:bool}
  PARAM_FLOAT           Positional float param {REQUIRED,type:float}
  PARAM_DOUBLE          Positional double param {REQUIRED,type:double}
  PARAMH                Positional repeating string params, there may be only
                        one repeating positional param {REQUIRED,type:string}

optional arguments:
  -h, --help            show this help message and exit
  -a paramA, --a-long-param paramA
                        String param option with default value. Note: this
                        comment will be taken as description
                        {OPTIONAL,type:string,default:"// tricky default
                        value"}
  --b-long-param paramB
                        Integer param with default value
                        {OPTIONAL,type:uint32,default:"10"}
  -c paramC, --c-long-param paramC
                        Integer param without default value. Avoid new lines
                        they are rendered not correctly in help. Words will be
                        transfered to new line anyway
                        {OPTIONAL,type:int32,default:""}
  --d-long-param paramD
                        Float param without default value
                        {OPTIONAL,type:float,default:""}
  -e paramE             String param which should be anyway
                        {REQUIRED,type:string,default:""}
  -f paramF [paramF ...]
                        Integer param which may encounter multiple times
                        {REPEATED,type:int32,default:""}
  -i                    Boolean arg with default value (despite it is declared
                        after positional args, that is not a problem)
                        {OPTIONAL,type:bool,default:"true"}
  --j-long              Boolean arg without default value
                        {OPTIONAL,type:bool,default:""}
  -k paramFloat         Float param {OPTIONAL,type:float,default:""}
  -l paramDouble        Double param {OPTIONAL,type:double,default:""}

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
function schema_parse() #(program, description, allow_incomplete, args)
{
    local program=$1
    local description=$2
    local allow_incomplete=$3

    schema_prepareOptions


    shift
    shift
    shift

    POSITIONAL_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in

            -a|--a-long-param)
                schema_paramA="$2"
                schema_paramA_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -a=*|--a-long-param=*)
                schema_paramA="${1#*=}"
                schema_paramA_PRESENT=true
                shift # past argument=value
                ;;

            --b-long-param)
                schema_paramB=$2
                schema_paramB_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --b-long-param=*)
                schema_paramB="${1#*=}"
                schema_paramB_PRESENT=true
                shift # past argument=value
                ;;

            -c|--c-long-param)
                schema_paramC=$2
                schema_paramC_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -c=*|--c-long-param=*)
                schema_paramC="${1#*=}"
                schema_paramC_PRESENT=true
                shift # past argument=value
                ;;

            --d-long-param)
                schema_paramD=$2
                schema_paramD_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            --d-long-param=*)
                schema_paramD="${1#*=}"
                schema_paramD_PRESENT=true
                shift # past argument=value
                ;;

            -e)
                schema_paramE="$2"
                schema_paramE_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -e=*)
                schema_paramE="${1#*=}"
                schema_paramE_PRESENT=true
                shift # past argument=value
                ;;

            -f)
                schema_paramF=$2
                schema_paramF_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -f=*)
                schema_paramF="${1#*=}"
                schema_paramF_PRESENT=true
                shift # past argument=value
                ;;

            -i)
                schema_param_I=true
                schema_param_I_PRESENT=true
                shift
                ;;

            --j-long)
                schema_param_J=true
                schema_param_J_PRESENT=true
                shift
                ;;

            -h|--help)
                schema_printHelp=true
                schema_printHelp_PRESENT=true
                shift
                ;;

            -k)
                schema_paramFloat=$2
                schema_paramFloat_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -k=*)
                schema_paramFloat="${1#*=}"
                schema_paramFloat_PRESENT=true
                shift # past argument=value
                ;;

            -l)
                schema_paramDouble=$2
                schema_paramDouble_PRESENT=true
                shift # past argument
                shift # past value
                ;;

            -l=*)
                schema_paramDouble="${1#*=}"
                schema_paramDouble_PRESENT=true
                shift # past argument=value
                ;;

            -*|--*)
                echo "Unknown option '$1'"
                schema_usage
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


        schema_PARAMG="${POSITIONAL_ARGS[0]}"
        if [ 0 -ge ${#POSITIONAL_ARGS[@]} ]; then
            echo "Positional 'PARAMG' parameter is not set"
            exit 1
        fi


        schema_PARAM_FLOAT="${POSITIONAL_ARGS[2]}"
        if [ 2 -ge ${#POSITIONAL_ARGS[@]} ]; then
            echo "Positional 'PARAM_FLOAT' parameter is not set"
            exit 1
        fi

        schema_PARAM_DOUBLE="${POSITIONAL_ARGS[3]}"
        if [ 3 -ge ${#POSITIONAL_ARGS[@]} ]; then
            echo "Positional 'PARAM_DOUBLE' parameter is not set"
            exit 1
        fi


    return 0
}

