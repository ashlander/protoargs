#!/bin/bash

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/bools_pa.sh

# common variables
program="test_bools.sh"
description="$(cat << PROTOARGS_EOM
Program description
    Test bools as they have a lot of edge cases
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
TEST_NAME="TestBoolsUsage" # no spaces allowed in test name
echo "${TEST_NAME}"
echo "##########################################"

bools_usage "${program}" "${description}"
if [ "$?" -eq 0 ]; then
    echo "${bools_PROTOARG_USAGE}"
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestBoolsConnectShortAndLongArgsTogether"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
        --rb \
        --reqbool \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    if [ "$bools_req_bool_PRESENT" != true ] || [ "$bools_req_bool" != true ]; then
        fail_line $LINENO
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestBoolsPositiveShort"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
        --rb \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$bools_req_bool_PRESENT" != true ] || [ "$bools_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_opt_bool_PRESENT" != false ] || [ "$bools_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_rep_bool_PRESENT" != false ] || [ "${#bools_rep_bool[@]}" -ne 0 ]  || [ "$bools_rep_bool_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ] || [ "$bools_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ] || [ "$bools_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != true ] || [ "${#bools_REOBOOL[@]}" -ne 3 ] || [ "$bools_REOBOOL_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestBoolsPositiveAll"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
        --rb \
        --optbool \
        --repbool false \
        --repbool true \
        --repbool false \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$bools_req_bool_PRESENT" != true ] || [ "$bools_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_opt_bool_PRESENT" != true ] || [ "$bools_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_rep_bool_PRESENT" != true ] || [ "${#bools_rep_bool[@]}" -ne 3 ]  || [ "$bools_rep_bool_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[0]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[1]}" != true ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[2]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ] || [ "$bools_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ] || [ "$bools_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != true ] || [ "${#bools_REOBOOL[@]}" -ne 3 ] || [ "$bools_REOBOOL_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestBoolsPositiveAllAllowed"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" true \
        --optbool \

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$bools_req_bool_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_opt_bool_PRESENT" != true ] || [ "$bools_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_rep_bool_PRESENT" != false ] || [ "${#bools_rep_bool[@]}" -ne 0 ] || [ "$bools_rep_bool_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != false ] || [ "${#bools_REOBOOL[@]}" -ne 0 ] || [ "$bools_REOBOOL_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestBoolsPositiveAllEquals"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
        --reqbool \
        --optbool \
        --repbool=false \
        --repbool=true \
        --repbool=false \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$bools_req_bool_PRESENT" != true ] || [ "$bools_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_opt_bool_PRESENT" != true ] || [ "$bools_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_rep_bool_PRESENT" != true ] || [ "${#bools_rep_bool[@]}" -ne 3 ]  || [ "$bools_rep_bool_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[0]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[1]}" != true ]; then
        fail_line $LINENO
    fi
    if [ "${bools_rep_bool[2]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ] || [ "$bools_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ] || [ "$bools_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != true ] || [ "${#bools_REOBOOL[@]}" -ne 3 ] || [ "$bools_REOBOOL_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMissingRequired"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
    false \
    false \
    false false false

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$bools_req_bool_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestMissingRepeatedPositional"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
    --reqbool \
    true \
    true

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$bools_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi


echo "##########################################"
NOK=false
TEST_NAME="TestPositionalWrongType"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" false \
    --reqbool \
    true \
    true \
    true true 1

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$bools_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalWrongTypeAllowed"
echo "${TEST_NAME}"
echo "##########################################"

bools_parse "${program}" "${description}" true \
    --reqbool \
    true \
    true \
    true true 1

if [ "$?" -eq 0 ]; then
    if [ "$bools_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$bools_REOBOOL_PRESENT" != true ]; then
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
    exit 1
fi
