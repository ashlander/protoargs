#!/bin/bash

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/position_types_pa.sh

# common variables
program="test_positional_types.sh"
description="$(cat << PROTOARGS_EOM
Program description
    Positional parameters should be correctly processed
    Type should be correctly checked
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
TEST_NAME="TestPositionalTypesUsage" # no spaces allowed in test name
echo "${TEST_NAME}"
echo "##########################################"

positional_types_usage "${program}" "${description}"
if [ "$?" -eq 0 ]; then
    echo "${positional_types_PROTOARGS_USAGE}"
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesConnectShortAndLongArgsTogether"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        --rb \
        --reqbool \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    if [ "$positional_types_req_bool_PRESENT" != true ] || [ "$positional_types_req_bool" != true ]; then
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
TEST_NAME="TestPositionalTypesPositiveShort"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        --rb \
        false \
        true \
        true false true

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$positional_types_req_bool_PRESENT" != true ] || [ "$positional_types_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_opt_bool_PRESENT" != false ] || [ "$positional_types_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_rep_bool_PRESENT" != false ] || [ "${#positional_types_rep_bool[@]}" -ne 0 ]  || [ "$positional_types_rep_bool_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ] || [ "$positional_types_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ] || [ "$positional_types_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != true ] || [ "${#positional_types_REOBOOL[@]}" -ne 3 ] || [ "$positional_types_REOBOOL_COUNT" -ne 3 ]; then
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
TEST_NAME="TestPositionalTypesPositiveAll"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
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
    if [ "$positional_types_req_bool_PRESENT" != true ] || [ "$positional_types_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_opt_bool_PRESENT" != true ] || [ "$positional_types_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_rep_bool_PRESENT" != true ] || [ "${#positional_types_rep_bool[@]}" -ne 3 ]  || [ "$positional_types_rep_bool_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[0]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[1]}" != true ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[2]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ] || [ "$positional_types_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ] || [ "$positional_types_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != true ] || [ "${#positional_types_REOBOOL[@]}" -ne 3 ] || [ "$positional_types_REOBOOL_COUNT" -ne 3 ]; then
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
TEST_NAME="TestPositionalTypesPositiveAllAllowed"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" true \
        --optbool \

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$positional_types_req_bool_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_opt_bool_PRESENT" != true ] || [ "$positional_types_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_rep_bool_PRESENT" != false ] || [ "${#positional_types_rep_bool[@]}" -ne 0 ] || [ "$positional_types_rep_bool_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != false ] || [ "${#positional_types_REOBOOL[@]}" -ne 0 ] || [ "$positional_types_REOBOOL_COUNT" -ne 0 ]; then
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
TEST_NAME="TestPositionalTypesPositiveAllEquals"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
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
    if [ "$positional_types_req_bool_PRESENT" != true ] || [ "$positional_types_req_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_opt_bool_PRESENT" != true ] || [ "$positional_types_opt_bool" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_rep_bool_PRESENT" != true ] || [ "${#positional_types_rep_bool[@]}" -ne 3 ]  || [ "$positional_types_rep_bool_COUNT" -ne 3 ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[0]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[1]}" != true ]; then
        fail_line $LINENO
    fi
    if [ "${positional_types_rep_bool[2]}" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ] || [ "$positional_types_OPTBOOL" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ] || [ "$positional_types_ALTBOOL" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != true ] || [ "${#positional_types_REOBOOL[@]}" -ne 3 ] || [ "$positional_types_REOBOOL_COUNT" -ne 3 ]; then
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
TEST_NAME="TestPositionalTypesMissingRequired"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
    false \
    false \
    false false false

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_req_bool_PRESENT" != false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesMissingRepeatedPositional"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
    --reqbool \
    true \
    true

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi


echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesPositionalWrongType"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
    --reqbool \
    true \
    true \
    true true 1

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != false ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesPositionalWrongTypeAllowed"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" true \
    --reqbool \
    true \
    true \
    true true 1

if [ "$?" -eq 0 ]; then
    if [ "$positional_types_req_bool_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_OPTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_ALTBOOL_PRESENT" != true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_REOBOOL_PRESENT" != true ]; then
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
