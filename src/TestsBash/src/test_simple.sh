#!/bin/bash

# find bash binary
bash=$(which bash)

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/simple_pa.sh

# common variables
program="test_simple.sh"
description="$(cat << PROTOARGS_EOM
Program description
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
TEST_NAME="TestSchemaUsage" # no spaces allowed in test name
echo "${TEST_NAME}"
echo "##########################################"

simple_usage "${program}" "${description}"
if [ "$?" -eq 0 ]; then
    echo "${simple_PROTOARG_USAGE}"
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestCheckAllPositiveEquals"
echo "${TEST_NAME}"
echo "##########################################"

simple_parse "${program}" "${description}" false \
        --count=2 \
        --configuration="/tmp/conf" \
        --flags=true \
        --flags=false \
        -c "flags should be true and false" \
        --o-underscore="no underscore" \
        --r-underscore="no underscore" \
        --a-underscore="no underscore0" \
        --a-underscore="no underscore1"

if [ "$?" -eq 0 ]; then
    if [ "$simple_count_PRESENT" != true ] || [ "$simple_count" != 2 ]; then
        fail_line $LINENO
    fi
    if [ "$simple_configuration_PRESENT" != true ] || [ "$simple_configuration" != "/tmp/conf" ]; then
        fail_line $LINENO
    fi
    if [ "$simple_flags_PRESENT" != true ] || [ "$simple_flags_COUNT" != 2 ]; then
        fail_line $LINENO
    fi
    if [ "${simple_flags[0]}" != true ]; then
        fail_line $LINENO
    fi
    if [ "${simple_flags[1]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "$simple_version_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$simple_help_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$simple_c_PRESENT" != true ] || [ "$simple_c" != "flags should be true and false" ]; then
        fail_line $LINENO
    fi
    if [ "$simple_o_underscore_PRESENT" != true ] || [ "$simple_o_underscore" != "no underscore" ]; then
        fail_line $LINENO
    fi
    if [ "$simple_r_underscore_PRESENT" != true ] || [ "$simple_r_underscore" != "no underscore" ]; then
        fail_line $LINENO
    fi
    if [ "$simple_a_underscore_PRESENT" != true ] || [ "$simple_a_underscore_COUNT" != 2 ]; then
        fail_line $LINENO
    fi
    if [ "${simple_a_underscore[0]}" != "no underscore0" ]; then
        fail_line $LINENO
    fi
    if [ "${simple_a_underscore[1]}" != "no underscore1" ]; then
        fail_line $LINENO
    fi
    if [ "$simple_s_quote_in_descr_PRESENT" != false ]; then
        fail_line $LINENO
    fi
else
    NOK=true
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
fi
