#!/bin/bash

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/positional_types_pa.sh

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
TEST_NAME="TestPositionalTypesPositiveAll"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        "Some string argument" \
        34 \
        1.454 \
        true

if [ "$?" -eq 0 ]; then
    if [ "$positional_types_STRING_PRESENT" == false ] || [ "$positional_types_STRING" != "Some string argument" ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == false ] || [ "$positional_types_INT32" -ne 34 ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == false ] || [ "$positional_types_FLOAT" != "1.454" ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == false ] || [ "$positional_types_BOOL" != true ]; then
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
        "Some string argument" \
        34

if [ "$?" -eq 0 ]; then
    if [ "$positional_types_STRING_PRESENT" == false ] || [ "$positional_types_STRING" != "Some string argument" ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == false ] || [ "$positional_types_INT32" -ne 34 ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == true ]; then
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
TEST_NAME="TestPositionalTypesPositionalWrongType"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        true \
        "Some string argument" \
        34 \
        1.454

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_STRING_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesPositionalWrongType2"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        "Some string argument" \
        34 \
        true \
        1.454

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_STRING_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestPositionalTypesPositionalWrongType3"
echo "${TEST_NAME}"
echo "##########################################"

positional_types_parse "${program}" "${description}" false \
        true \
        34 \
        1.454 \
        "Some string argument"

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$positional_types_STRING_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == true ]; then
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
        true \
        "Some string argument" \
        34 \
        1.454

if [ "$?" -eq 0 ]; then
    if [ "$positional_types_STRING_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_INT32_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_FLOAT_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$positional_types_BOOL_PRESENT" == true ]; then
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
