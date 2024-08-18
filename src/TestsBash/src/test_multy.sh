#!/bin/bash

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/multy_command_pa.sh
. $SCRIPTPATH/multy_command_copy_pa.sh
. $SCRIPTPATH/multy_command_create_pa.sh

# common variables
program="test_multy.sh"
description="$(cat << PROTOARGS_EOM
Program description
    Testing multi argument constructions
    and another line of description
    and biiiggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg line of description
    well, and another one with extra junk
PROTOARGS_EOM
)"

# register failures
FAILED=()
function fail()
{
    local message="[NOK] ${TEST_NAME}"
    echo "${message}"
    FAILED+=("${message}")
}

function fail_line()
{
    line=$1
    local message="--- /line:${line}/"
    echo "${message}"
    FAILED+=("${message}")
    NOK=true
}

# output failures
function print_failed()
{
    for i in "${FAILED[@]}"
    do
       echo "$i"
    done
}


echo "##########################################"
NOK=false
TEST_NAME="TestMultyUsage" # no spaces allowed in test name
echo "${TEST_NAME}"
echo "##########################################"

multy_command_usage "${program}" "${description}"
if [ "$?" -eq 0 ]; then
    echo "${multy_command_PROTOARGS_USAGE}"
else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMultyCommandsUsage"
echo "${TEST_NAME}"
echo "##########################################"

multy_command_usage "${program}" "${description}" \
    -h

if [ "$?" -eq 0 ]; then
    echo "${multy_command_PROTOARGS_USAGE}"
else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMultyCommandsCreateUsage"
echo "${TEST_NAME}"
echo "##########################################"

args=()
args+=("create")
args+=("-h")

# remove all other except for COMMAND and posiible -h
multy_command_remove_args_tail 1 $args
multy_command_parse "${program}" "${description}" false \
    $multy_command_PROTOARGS_ARGS

if [ "$?" -eq 0 ]; then
    if [ "$multy_command_COMMAND_PRESENT" != true ] || [ "$multy_command_COMMAND" != "create" ]; then
        fail_line $LINENO
    else
        # remove COMMAND from arguments
        multy_command_keep_args_tail 1 "${args[@]}"
        echo args=$args
        echo pargs=$multy_command_PROTOARGS_ARGS

        # check first for possible help with allow_incomplete
        multy_command_create_parse "${program}" "${description}" true \
            $multy_command_PROTOARGS_ARGS

        if [ "$?" -eq 0 ]; then
            if [ "$multy_command_create_help_PRESENT" != true ] || [ "$multy_command_create_help" != true ]; then
                fail_line $LINENO
            fi

            multy_command_create_usage "${program}" "${description}"
            echo "$multy_command_create_PROTOARGS_USAGE"
        else
            fail_line $LINENO
        fi
    fi

else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMultyCheckAllPositiveCreate"
echo "${TEST_NAME}"
echo "##########################################"

args=()
args+=("create")
args+=("-s")
args+=("2048")
args+=("/tmp/tmp.file")

# remove all other except for COMMAND and posiible -h
multy_command_remove_args_tail 1 "${args[@]}"
multy_command_parse "${program}" "${description}" false \
    "${multy_command_PROTOARGS_ARGS[@]}"

if [ "$?" -eq 0 ]; then
    if [ "$multy_command_COMMAND_PRESENT" != true ] || [ "$multy_command_COMMAND" != "create" ]; then
        fail_line $LINENO
    else
        # remove COMMAND from arguments
        multy_command_keep_args_tail 1 "${args[@]}"

        # check first for possible help with allow_incomplete
        multy_command_create_parse "${program}" "${description}" true \
            "${multy_command_PROTOARGS_ARGS[@]}"

        if [ "$?" -eq 0 ]; then
            if [ "$multy_command_create_help_PRESENT" != false ] || [ "$multy_command_create_help" != false ]; then
                fail_line $LINENO
            fi
            if [ "$multy_command_create_size_PRESENT" != true ] || [ "$multy_command_create_size" -ne 2048 ]; then
                fail_line $LINENO
            fi
            if [ "$multy_command_create_PATH_PRESENT" != true ] || [ "$multy_command_create_PATH" != "/tmp/tmp.file" ]; then
                fail_line $LINENO
            fi
        else
            fail_line $LINENO
        fi
    fi

else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMultyCommandsCopyUsage"
echo "${TEST_NAME}"
echo "##########################################"

args=()
args+=("copy")
args+=("-h")

# remove all other except for COMMAND and posiible -h
multy_command_remove_args_tail 1 "${args[@]}"
multy_command_parse "${program}" "${description}" false \
    "${multy_command_PROTOARGS_ARGS[@]}"

if [ "$?" -eq 0 ]; then
    if [ "$multy_command_COMMAND_PRESENT" != true ] || [ "$multy_command_COMMAND" != "copy" ]; then
        fail_line $LINENO
    else
        # remove COMMAND from arguments
        multy_command_keep_args_tail 1 "${args[@]}"

        # check first for possible help with allow_incomplete
        multy_command_copy_parse "${program}" "${description}" true \
            "${multy_command_PROTOARGS_ARGS[@]}"

        if [ "$?" -eq 0 ]; then
            if [ "$multy_command_copy_help_PRESENT" != true ] || [ "$multy_command_copy_help" != true ]; then
                fail_line $LINENO
            fi

            multy_command_copy_usage "${program}" "${description}"
            echo "$multy_command_copy_PROTOARGS_USAGE"
        else
            fail_line $LINENO
        fi
    fi

else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMultyCheckAllPositiveCopy"
echo "${TEST_NAME}"
echo "##########################################"

args=()
args+=("copy")
args+=("-r")
args+=("/tmp/tmp 0.file.src")
args+=("/tmp/tmp 1.file.dst")

# remove all other except for COMMAND and posiible -h
multy_command_remove_args_tail 1 "${args[@]}"
multy_command_parse "${program}" "${description}" false \
    "${multy_command_PROTOARGS_ARGS[@]}"

if [ "$?" -eq 0 ]; then
    if [ "$multy_command_COMMAND_PRESENT" != true ] || [ "$multy_command_COMMAND" != "copy" ]; then
        fail_line $LINENO
    else
        # remove COMMAND from arguments
        multy_command_keep_args_tail 1 "${args[@]}"

        # check first for possible help with allow_incomplete
        multy_command_copy_parse "${program}" "${description}" true \
            "${multy_command_PROTOARGS_ARGS[@]}"

        if [ "$?" -eq 0 ]; then
            if [ "$multy_command_copy_help_PRESENT" != false ] || [ "$multy_command_copy_help" != false ]; then
                fail_line $LINENO
            fi
            if [ "$multy_command_copy_recursive_PRESENT" != true ] || [ "$multy_command_copy_recursive" != true ]; then
                fail_line $LINENO
            fi
            if [ "$multy_command_copy_SRC_PRESENT" != true ] || [ "$multy_command_copy_SRC" != "/tmp/tmp 0.file.src" ]; then
                fail_line $LINENO
            fi
            if [ "$multy_command_copy_DST_PRESENT" != true ] || [ "$multy_command_copy_DST" != "/tmp/tmp 1.file.dst" ]; then
                fail_line $LINENO
            fi
        else
            fail_line $LINENO
        fi
    fi

else
    fail_line $LINENO
fi
if [ "$NOK" == true ]; then
    fail
fi


#############################################################
# Failures summary
#############################################################
if [ "${#FAILED[@]}" -gt 0 ]; then
    echo "================= SUMMARY ========================="
    print_failed
    echo "==================================================="
    exit 1
fi
