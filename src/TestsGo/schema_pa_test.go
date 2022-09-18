package main

import (
    "fmt"
    "testing"
    "strings"
    "./schema_pa"
)

func TestSimpleUsage(t *testing.T) {
    description := "Desription"
    argv := []string{"program", "--help"}

    // check usage
    usage := schema_pa.Usage(argv[0], description)
    if len( strings.TrimSpace(usage) ) == 0 {
        t.Fatalf(`SimpleUsage: usage is empty`)
    }
}

func TestConnectShortAndLongArgsTogether(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "-e", "valueE",
        "--a-long-param", "somevalue", // inside only '-a' is analized
        "50", // paramG
        "true", // bool P-A-R-A-M-G-2
        "0.5", // PARAM-FLOAT
        "0.7", // PARAM-DOUBLE
        "pos1", "pos2", "pos3",
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err != nil {
        t.Fatalf(`SchemaUsage: %s`, err)
    }

    if config.ArgparamA.IsSet() != true && config.ArgparamA.Get() == `somevalue` {
        t.Fatalf(`SchemaUsage: 'paramA' is %s, expected 'somevalue'`, config.ArgparamA.Get())
    }
}

func TestSchemaPositiveShort(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "-e", "valueE",
        "50", // paramG
        "false", // bool P-A-R-A-M-G-2
        "0.5", // PARAM-FLOAT
        "0.7", // PARAM-DOUBLE
        "pos1", "pos2", "pos3",
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err != nil {
        t.Fatalf(`SchemaUsage: %s`, err)
    }

    // check defaults
    if config.ArgparamA.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'paramA' expected to be not set`)
    }
    if config.ArgparamA.Get() != `// tricky default value` {
        t.Fatalf(`SchemaUsage: 'paramA' is %s, expected '// tricky default value'`, config.ArgparamA.Get())
    }

    if config.ArgparamB.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'paramB' expected to be not set`)
    }
    if config.ArgparamB.Get() != 10 {
        t.Fatalf(`SchemaUsage: 'paramB' is %d, expected 10`, config.ArgparamB.Get())
    }

    if config.ArgparamC.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'paramC' expected to be not set`)
    }
    if config.ArgparamC.Get() != 0 {
        t.Fatalf(`SchemaUsage: 'paramC' is %d, expected 0`, config.ArgparamC.Get())
    }

    if config.ArgparamD.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'paramD' expected to be not set`)
    }
    if config.ArgparamD.Get() != 0.0 {
        t.Fatalf(`SchemaUsage: 'paramD' is %f, expected 0.0`, config.ArgparamD.Get())
    }

    if config.ArgparamE.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramE' expected to be set`)
    }
    if config.ArgparamE.Get() != `valueE` {
        t.Fatalf(`SchemaUsage: 'paramE' is %s, expected 'valueE'`, config.ArgparamE.Get())
    }

    if len(config.ArgparamF) != 0 {
        t.Fatalf(`SchemaUsage: 'paramF' len is %d, expected 0`, len(config.ArgparamF))
    }

    if config.Argparam_I.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'param_I' expected to be not set`)
    }
    if config.Argparam_I.Get() != true {
        t.Fatalf(`SchemaUsage: 'param_I' is %t, expected true`, config.Argparam_I.Get())
    }

    if config.Argparam_J.IsSet() == true {
        t.Fatalf(`SchemaUsage: 'param_J' expected to be not set`)
    }
    if config.Argparam_J.Get() != false {
        t.Fatalf(`SchemaUsage: 'param_J' is %t, expected true`, config.Argparam_J.Get())
    }

    if len(config.ArgPARAMH) != 3 {
        t.Fatalf(`SchemaUsage: 'PARAMH' len is %d, expected 0`, len(config.ArgPARAMH))
    }
}

func TestSchemaPositiveAll(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
         "-e", "valueE",
         "--a-long-param", "somevalue",
         "--b-long-param", "4",
         "-c", "555",
         "--d-long-param", "555.5",
         "-f", "1",
         "-f", "2",
         "-f", "3",
         "-i",
         "--j-long",
         "50", // paramG
         "false", // bool paramG
         "0.5", // PARAM-FLOAT
         "0.7", // PARAM-DOUBLE
         "pos1", "pos2", "pos3", // paramH
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err != nil {
        t.Fatalf(`SchemaUsage: %s`, err)
    }

    // check defaults
    if config.ArgparamA.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramA' expected to be set`)
    }
    if config.ArgparamA.Get() != `somevalue` {
        t.Fatalf(`SchemaUsage: 'paramA' is %s, expected 'somevalue'`, config.ArgparamA.Get())
    }

    if config.ArgparamB.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramB' expected to be set`)
    }
    if config.ArgparamB.Get() != 4 {
        t.Fatalf(`SchemaUsage: 'paramB' is %d, expected 4`, config.ArgparamB.Get())
    }

    if config.ArgparamC.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramC' expected to be set`)
    }
    if config.ArgparamC.Get() != 555 {
        t.Fatalf(`SchemaUsage: 'paramC' is %d, expected 555`, config.ArgparamC.Get())
    }

    if config.ArgparamD.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramD' expected to be set`)
    }
    if config.ArgparamD.Get() != 555.5 {
        t.Fatalf(`SchemaUsage: 'paramD' is %f, expected 555.5`, config.ArgparamD.Get())
    }

    if config.ArgparamE.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'paramE' expected to be set`)
    }
    if config.ArgparamE.Get() != `valueE` {
        t.Fatalf(`SchemaUsage: 'paramE' is %s, expected 'valueE'`, config.ArgparamE.Get())
    }

    if len(config.ArgparamF) != 3 {
        t.Fatalf(`SchemaUsage: 'paramF' len is %d, expected 3`, len(config.ArgparamF))
    }

    if config.Argparam_I.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'param_I' expected to be set`)
    }
    if config.Argparam_I.Get() != true {
        t.Fatalf(`SchemaUsage: 'param_I' is %t, expected true`, config.Argparam_I.Get())
    }

    if config.Argparam_J.IsSet() != true {
        t.Fatalf(`SchemaUsage: 'param_J' expected to be set`)
    }
    if config.Argparam_J.Get() != true {
        t.Fatalf(`SchemaUsage: 'param_J' is %t, expected true`, config.Argparam_J.Get())
    }

    if len(config.ArgPARAMH) != 3 {
        t.Fatalf(`SchemaUsage: 'PARAMH' len is %d, expected 0`, len(config.ArgPARAMH))
    }
}

func TestMissingRequired(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "50", // paramG
        "0", // bool paramG
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err == nil {
        fmt.Println(config)
        t.Fatalf(`SchemaUsage: Expected to fail`)
    }
}

func TestMissingRepeatedPositional(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "-e", "valueE",
        "50", // paramG
        "true", // bool paramG
        "0.5", // PARAM-FLOAT
        "0.7", // PARAM-DOUBLE
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err == nil {
        fmt.Println(config)
        t.Fatalf(`SchemaUsage: Expected to fail`)
    }
}

func TestPositionalWrongType(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "-e", "valueE",
        "50f", // paramG
        "0e", // bool paramG
        "0.5d", // PARAM-FLOAT
        "0.7d", // PARAM-DOUBLE
        "pos1", "pos2", "pos3",
    }

    config, err := schema_pa.ParseExt(argv[0], argv, description, false)

    if err == nil {
        fmt.Println(config)
        t.Fatalf(`SchemaUsage: Expected to fail`)
    }
}

