package main

import (
    "fmt"
    "testing"
    "strings"
    "./simple_pa"
)

func TestSchemaUsage(t *testing.T) {
    description := "Desription"
    argv := []string{"program", "--help"}

    // check usage
    usage := simple_pa.Usage(argv[0], description)
    if len( strings.TrimSpace(usage) ) == 0 {
        t.Fatalf(`SimpleUsage: usage is empty`)
    }
}

func TestCheckAllPositive(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "--count", "1",
        "--configuration", "/tmp/conf",
        "--flags", "true",
        "--flags", "false",
        "-c", "flags should be true and false",
        "--o-underscore", "no underscore",
        "--r-underscore", "no underscore",
        "--a-underscore", "no underscore0",
        "--a-underscore", "no underscore1",
    }

    config, err := simple_pa.ParseExt(argv[0], argv, description, false)

    if err != nil {
        t.Fatalf(`SimpleUsage: %s`, err)
    }

    if config.Argcount.Get() != 1 {
        t.Fatalf(`SimpleUsage: 'count' is %d, expected 1`, config.Argcount.Get())
    }

    if config.Argconfiguration.Get() != `/tmp/conf` {
        t.Fatalf(`SimpleUsage: 'configuration' is %s, expected '/tmp/conf'`, config.Argconfiguration.Get())
    }

    if len(config.Argflags) != 2 {
        t.Fatalf(`SimpleUsage: len of 'flags' is %d, expected 2 => %s`, len(config.Argflags), config.Argflags.String())
    }
    if config.Argflags[0] != true {
        t.Fatalf(`SimpleUsage: 'flags' are %s, expected other`, config.Argflags.String())
    }
    if config.Argflags[1] != false {
        t.Fatalf(`SimpleUsage: 'flags' are %s, expected other`, config.Argflags.String())
    }

    if config.Argc.Get() != `flags should be true and false` {
        t.Fatalf(`SimpleUsage: 'configuration' is %s, expected 'flags should be true and false'`, config.Argc.Get())
    }

    if config.Argr_underscore.Get() != `no underscore` {
        t.Fatalf(`SimpleUsage: 'r_underscore' is %s, expected 'no underscore'`, config.Argr_underscore.Get())
    }

    if config.Argo_underscore.Get() != `no underscore` {
        t.Fatalf(`SimpleUsage: 'o_underscore' is %s, expected 'no underscore'`, config.Argo_underscore.Get())
    }

    if len(config.Arga_underscore) != 2 {
        t.Fatalf(`SimpleUsage: len of 'a_underscore' is %d, expected 2 => %s`, len(config.Arga_underscore), config.Arga_underscore.String())
    }
    if config.Arga_underscore[0] != "no underscore0" {
        t.Fatalf(`SimpleUsage: 'a_underscore' are %s, expected other`, config.Arga_underscore.String())
    }
    if config.Arga_underscore[1] != "no underscore1" {
        t.Fatalf(`SimpleUsage: 'a_underscore' are %s, expected other`, config.Arga_underscore.String())
    }
}

// trailing positional will be skipped
func TestCheckNoPositional(t *testing.T) {
    description := "Desription"
    argv := []string{
       "program",
       "--count", "1",
       "--configuration", "/tmp/conf",
       "--flags", "true",
       "--flags", "false",
       "-c", "flags should be true and false",
       "--r-underscore", "no underscore",
       "positional_value",
       "positional_value",
       "positional_value",
       "positional_value",
       "positional_value",
    }

    config, err := simple_pa.ParseExt(argv[0], argv, description, false)

    if err != nil {
        t.Fatalf(`SimpleUsage: %s`, err)
    }

    if config.Argcount.Get() != 1 {
        t.Fatalf(`SimpleUsage: 'count' is %d, expected 1`, config.Argcount.Get())
    }

    if config.Argconfiguration.Get() != `/tmp/conf` {
        t.Fatalf(`SimpleUsage: 'configuration' is %s, expected '/tmp/conf'`, config.Argconfiguration.Get())
    }

    if len(config.Argflags) != 2 {
        t.Fatalf(`SimpleUsage: len of 'flags' is %d, expected 2 => %s`, len(config.Argflags), config.Argflags.String())
    }
    if config.Argflags[0] != true {
        t.Fatalf(`SimpleUsage: 'flags' are %s, expected other`, config.Argflags.String())
    }
    if config.Argflags[1] != false {
        t.Fatalf(`SimpleUsage: 'flags' are %s, expected other`, config.Argflags.String())
    }

    if config.Argc.Get() != `flags should be true and false` {
        t.Fatalf(`SimpleUsage: 'configuration' is %s, expected 'flags should be true and false'`, config.Argc.Get())
    }
}

func TestCheckWrongType(t *testing.T) {
    description := "Desription"
    argv := []string{
       "program",
       "--count", "stringnotdigit",
       "--configuration", "/tmp/conf",
       "--flags", "true",
       "--flags", "false",
       "-c", "flags should be true and false",
       "--r-underscore", "no underscore",
    }

    config, err := simple_pa.ParseExt(argv[0], argv, description, false)

    if err == nil {
        fmt.Println(config)
        t.Fatalf(`SimpleUsage: Expect error here because of type mismatch`)
    }
}
