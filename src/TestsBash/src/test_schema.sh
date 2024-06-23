#!/bin/bash

# include parser
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
. $SCRIPTPATH/schema_pa.sh

# common variables
program="test_schema.sh"
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

schema_usage "${program}" "${description}"
if [ "$?" -eq 0 ]; then
    echo "${schema_PROTOARGS_USAGE}"
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaConnectShortAndLongArgsTogether"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
        -e "valueE" \
        --a-long-param "somevalue" \
        50 \
        true \
        0.5 \
        0.7 \
        "pos1" "pos2" "pos3"

if [ "$?" -eq 0 ]; then
    if [ "$schema_paramA_PRESENT" != true ] || [ "$schema_paramA" != "somevalue" ]; then
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
TEST_NAME="TestSchemaPositiveShort"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
        -e "valueE" \
        50 \
        false \
        0.5 \
        0.7 \
        "pos1" "pos2" "pos3"

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$schema_paramA_PRESENT" == true ] || [ "$schema_paramA" != "// tricky default value" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramB_PRESENT " == true ] || [ "$schema_paramB" -ne 10 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramC_PRESENT" == true ] || [ "$schema_paramC" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramD_PRESENT" == true ] || [ $(echo "$schema_paramD == 0.0" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramE_PRESENT" == false ] || [ "$schema_paramE" != "valueE" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramF_PRESENT" == true ] || [ "${#schema_paramF[@]}" -ne 0 ] || [ "$schema_paramF_COUNT" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_I_PRESENT" == true ] || [ "$schema_param_I" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_J_PRESENT" == true ] || [ "$schema_param_J" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ] || [ "${#schema_PARAMH[@]}" -ne 3 ] || [ "$schema_PARAMH_COUNT" -ne 3 ]; then
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
TEST_NAME="TestSchemaPositiveAll"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
         -e "valueE" \
         --a-long-param "somevalue" \
         --b-long-param 4 \
         -c 555 \
         --d-long-param 555.5 \
         -f 1 \
         -f 2 \
         -f 3 \
         -i \
         --j-long \
         50 \
         false \
         0.5 \
         0.7 \
         pos1 pos2 pos3

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$schema_paramA_PRESENT" == false ] || [ "$schema_paramA" != "somevalue" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramB_PRESENT " == false ] || [ "$schema_paramB" -ne 4 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramC_PRESENT" == false ] || [ "$schema_paramC" -ne 555 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramD_PRESENT" == false ] || [ $(echo "$schema_paramD == 555.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramE_PRESENT" == false ] || [ "$schema_paramE" != "valueE" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramF_PRESENT" == false ] || [ "${#schema_paramF[@]}" -ne 3 ] || [ "$schema_paramF_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_paramF[0]}" -ne 1 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[1]}" -ne 2 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[2]}" -ne 3 ]; then
            fail_line $LINENO
        fi
    fi
    if [ "$schema_param_I_PRESENT" == false ] || [ "$schema_param_I" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_J_PRESENT" == false ] || [ "$schema_param_J" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == false ] || [ $(echo "$schema_PARAM_FLOAT == 0.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == false ] || [ $(echo "$schema_PARAM_DOUBLE == 0.7" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ] || [ "${#schema_PARAMH[@]}" -ne 3 ] || [ "$schema_PARAMH_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_PARAMH[0]}" != "pos1" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[1]}" != "pos2" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[2]}" != "pos3" ]; then
            fail_line $LINENO
        fi
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaPositiveAllAllowed"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" true \
         -e "valueE" \
         --a-long-param "somevalue" \
         --b-long-param 4 \
         -c 555ergerg \
         --d-long-param 555.5 \
         -f 1 \
         -f 2 \
         -f 3 \
         -i \
         --j-long \
         50 \
         false \
         0.5 \
         0.7 \
         pos1 pos2 pos3

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$schema_paramA_PRESENT" == false ] || [ "$schema_paramA" != "somevalue" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramB_PRESENT " == false ] || [ "$schema_paramB" -ne 4 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramC_PRESENT" == false ] || [ "$schema_paramC" -ne 0 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramD_PRESENT" == false ] || [ $(echo "$schema_paramD == 555.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramE_PRESENT" == false ] || [ "$schema_paramE" != "valueE" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramF_PRESENT" == false ] || [ "${#schema_paramF[@]}" -ne 3 ] || [ "$schema_paramF_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_paramF[0]}" -ne 1 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[1]}" -ne 2 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[2]}" -ne 3 ]; then
            fail_line $LINENO
        fi
    fi
    if [ "$schema_param_I_PRESENT" == false ] || [ "$schema_param_I" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_J_PRESENT" == false ] || [ "$schema_param_J" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == false ] || [ $(echo "$schema_PARAM_FLOAT == 0.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == false ] || [ $(echo "$schema_PARAM_DOUBLE == 0.7" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ] || [ "${#schema_PARAMH[@]}" -ne 3 ] || [ "$schema_PARAMH_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_PARAMH[0]}" != "pos1" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[1]}" != "pos2" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[2]}" != "pos3" ]; then
            fail_line $LINENO
        fi
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi


echo "##########################################"
NOK=false
TEST_NAME="TestSchemaPositiveAllEquals"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
         -e="valueE" \
         --a-long-param="somevalue" \
         --b-long-param=4 \
         -c=555 \
         --d-long-param=555.5 \
         -f=1 \
         -f=2 \
         -f=3 \
         -i \
         --j-long \
         50 \
         false \
         0.5 \
         0.7 \
         pos1 pos2 pos3

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$schema_paramA_PRESENT" == false ] || [ "$schema_paramA" != "somevalue" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramB_PRESENT " == false ] || [ "$schema_paramB" -ne 4 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramC_PRESENT" == false ] || [ "$schema_paramC" -ne 555 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramD_PRESENT" == false ] || [ $(echo "$schema_paramD == 555.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramE_PRESENT" == false ] || [ "$schema_paramE" != "valueE" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramF_PRESENT" == false ] || [ "${#schema_paramF[@]}" -ne 3 ] || [ "$schema_paramF_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_paramF[0]}" -ne 1 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[1]}" -ne 2 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[2]}" -ne 3 ]; then
            fail_line $LINENO
        fi
    fi
    if [ "$schema_param_I_PRESENT" == false ] || [ "$schema_param_I" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_J_PRESENT" == false ] || [ "$schema_param_J" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == false ] || [ $(echo "$schema_PARAM_FLOAT == 0.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == false ] || [ $(echo "$schema_PARAM_DOUBLE == 0.7" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ] || [ "${#schema_PARAMH[@]}" -ne 3 ] || [ "$schema_PARAMH_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_PARAMH[0]}" != "pos1" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[1]}" != "pos2" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[2]}" != "pos3" ]; then
            fail_line $LINENO
        fi
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaPositiveAllEqualsMinus"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
         -e="valueE" \
         --a-long-param="somevalue" \
         --b-long-param=4 \
         -c=-555 \
         --d-long-param=-555.5 \
         -f=-1 \
         -f=-2 \
         -f=-3 \
         -i \
         --j-long \
         50 \
         false \
         -0.5 \
         -0.7 \
         pos1 pos2 pos3

if [ "$?" -eq 0 ]; then
    # check defaults
    if [ "$schema_paramA_PRESENT" == false ] || [ "$schema_paramA" != "somevalue" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramB_PRESENT " == false ] || [ "$schema_paramB" -ne 4 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramC_PRESENT" == false ] || [ "$schema_paramC" -ne -555 ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramD_PRESENT" == false ] || [ $(echo "$schema_paramD == -555.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramE_PRESENT" == false ] || [ "$schema_paramE" != "valueE" ]; then
        fail_line $LINENO
    fi
    if [ "$schema_paramF_PRESENT" == false ] || [ "${#schema_paramF[@]}" -ne 3 ] || [ "$schema_paramF_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_paramF[0]}" -ne -1 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[1]}" -ne -2 ]; then
            fail_line $LINENO
        fi
        if [ "${schema_paramF[2]}" -ne -3 ]; then
            fail_line $LINENO
        fi
    fi
    if [ "$schema_param_I_PRESENT" == false ] || [ "$schema_param_I" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_param_J_PRESENT" == false ] || [ "$schema_param_J" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == false ] || [ $(echo "$schema_PARAM_FLOAT == -0.5" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == false ] || [ $(echo "$schema_PARAM_DOUBLE == -0.7" | bc -l) == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ] || [ "${#schema_PARAMH[@]}" -ne 3 ] || [ "$schema_PARAMH_COUNT" -ne 3 ]; then
        fail_line $LINENO
    else
        if [ "${schema_PARAMH[0]}" != "pos1" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[1]}" != "pos2" ]; then
            fail_line $LINENO
        fi
        if [ "${schema_PARAMH[2]}" != "pos3" ]; then
            fail_line $LINENO
        fi
    fi
else
    NOK=true
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaMissingRequired"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
        50 \
        0

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$schema_PARAMG_PRESENT " == false ]; then
        fail_line $LINENO
    fi
    # 0 is not false
    if [ "$schema_P_A_R_A_M_G_2_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaMissingRepeatedPositional"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" false \
        -e "valueE" \
        50 \
        true \
        0.5 \
        0.7

if [ "$?" -eq 0 ]; then
    NOK=true
else
    if [ "$schema_PARAMG_PRESENT " == false ]; then
        fail_line $LINENO
    fi
    # 0 is not false
    if [ "$schema_P_A_R_A_M_G_2_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == false ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == true ]; then
        fail_line $LINENO
    fi
fi
if [ "$NOK" == true ]; then
    fail
fi

echo "##########################################"
NOK=false
TEST_NAME="TestSchemaPositionalWrongType"
echo "${TEST_NAME}"
echo "##########################################"

schema_parse "${program}" "${description}" true \
        -e "valueE" \
        50f \
        0e \
        0.5d \
        0.7d \
        "pos1" "pos2" "pos3"

if [ "$?" -eq 0 ]; then
    if [ "$schema_PARAMG_PRESENT " == true ]; then
        fail_line $LINENO
    fi
    # 0 is not false
    if [ "$schema_P_A_R_A_M_G_2_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_FLOAT_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAM_DOUBLE_PRESENT" == true ]; then
        fail_line $LINENO
    fi
    if [ "$schema_PARAMH_PRESENT" == false ]; then
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
