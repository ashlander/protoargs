package main

import (
    "fmt"
    "testing"
    "strings"
    "./multy_command_pa"
    "./multy_command_create_pa"
    "./multy_command_copy_pa"
)

func TestMultyCommandsUsage(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "-h",
    }

    // check usage
    usage := multy_command_pa.Usage(argv[0], description)
    if len( strings.TrimSpace(usage) ) == 0 {
        t.Fatalf(`MultyUsage: usage is empty`)
    }

    config, err := multy_command_pa.ParseExt(argv[0], argv, description, true)

    if err != nil {
        fmt.Println(config)
        t.Fatalf(`MultyUsage: %s`, err)
    }

    fmt.Println(usage)
}

func TestMultiCommandsCreateUsage(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "create",
        "-h",
    }

    program := argv[0]
    command := ""

    { // check main args
        config, err := multy_command_pa.ParseExt(program, argv[:2], description, false) // parse only 2 first arguments, that will be command name only

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.ArgCOMMAND.Get() != `create` {
            t.Fatalf(`MultyUsage: Command is %s but expected 'create'`, config.ArgCOMMAND.Get())
        }

        command = config.ArgCOMMAND.Get()
    }

    { // check create args
        program += " " + command
        argv_nocmd := append(argv[:1], argv[2:]...) // remove command name from arguments

        config, err := multy_command_create_pa.ParseExt(program, argv_nocmd, description, true)

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.Arghelp.IsSet() != true {
            t.Fatalf(`MultyUsage: Expected help argument specified for create command`)
        }

        // check usage
        usage := multy_command_create_pa.Usage(program, description)
        if len( strings.TrimSpace(usage) ) == 0 {
            t.Fatalf(`MultyUsage: usage is empty`)
        }
    }
}

func TestCheckAllPositiveCreate(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
         "create",
        "-s", "2048",
         "/tmp/tmp.file",
    }

    program := argv[0]
    command := ""

    { // check main args
        config, err := multy_command_pa.ParseExt(program, argv[:2], description, false) // parse only 2 first arguments, that will command name only

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.ArgCOMMAND.Get() != `create` {
            t.Fatalf(`MultyUsage: Command is %s but expected 'create'`, config.ArgCOMMAND.Get())
        }

        command = config.ArgCOMMAND.Get()
    }

    { // check create args
        program += " " + command
        argv_nocmd := append(argv[:1], argv[2:]...) // remove command name from arguments

        config, err := multy_command_create_pa.ParseExt(program, argv_nocmd, description, false)

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.Argsize.IsSet() != true {
            t.Fatalf(`MultyUsage: 'size' expected to be set`)
        }
        if config.Argsize.Get() != 2048 {
            t.Fatalf(`MultyUsage: 'size' is %d, expected 2048`, config.Argsize.Get())
        }

        if config.ArgPATH.IsSet() != true {
            t.Fatalf(`MultyUsage: 'PATH' expected to be set`)
        }
        if config.ArgPATH.Get() != `/tmp/tmp.file` {
            t.Fatalf(`MultyUsage: 'PATH' is %s, expected '/tmp/tmp.file'`, config.ArgPATH.Get())
        }
    }
}

func TestMultiCommandsCopyUsage(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "copy",
        "-h",
    }

    program := argv[0]
    command := ""

    { // check main args
        config, err := multy_command_pa.ParseExt(program, argv[:2], description, false) // parse only 2 first arguments, that will be command name without the rest

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.ArgCOMMAND.Get() != `copy` {
            t.Fatalf(`MultyUsage: Command is %s but expected 'copy'`, config.ArgCOMMAND.Get())
        }

        command = config.ArgCOMMAND.Get()
    }

    { // check create args
        program += " " + command
        argv_nocmd := append(argv[:1], argv[2:]...) // remove command name from arguments

        config, err := multy_command_copy_pa.ParseExt(program, argv_nocmd, description, true)

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.Arghelp.IsSet() != true {
            t.Fatalf(`MultyUsage: Expected help argument specified for create command`)
        }

        // check usage
        usage := multy_command_copy_pa.Usage(program, description)
        if len( strings.TrimSpace(usage) ) == 0 {
            t.Fatalf(`MultyUsage: usage is empty`)
        }
    }
}

func TestCheckAllPositiveCopy(t *testing.T) {
    description := "Desription"
    argv := []string{
        "program",
        "copy",
        "-r",
        "/tmp/tmp.file.src",
        "/tmp/tmp.file.dst",
    }

    program := argv[0]
    command := ""

    { // check main args
        config, err := multy_command_pa.ParseExt(program, argv[:2], description, false) // parse only 2 first arguments, that will command name only

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.ArgCOMMAND.Get() != `copy` {
            t.Fatalf(`MultyUsage: Command is %s but expected 'copy'`, config.ArgCOMMAND.Get())
        }

        command = config.ArgCOMMAND.Get()
    }

    { // check copy args
        program += " " + command
        argv_nocmd := append(argv[:1], argv[2:]...) // remove command name from arguments

        config, err := multy_command_copy_pa.ParseExt(program, argv_nocmd, description, false)

        if err != nil {
            t.Fatalf(`MultyUsage: %s`, err)
        }

        if config.Argrecursive.IsSet() != true {
            t.Fatalf(`MultyUsage: 'recursive' expected to be set`)
        }
        if config.Argrecursive.Get() != true {
            t.Fatalf(`MultyUsage: 'recursive' is %t, expected true`, config.Argrecursive.Get())
        }

        if config.ArgSRC.IsSet() != true {
            t.Fatalf(`MultyUsage: 'SRC' expected to be set`)
        }
        if config.ArgSRC.Get() != `/tmp/tmp.file.src` {
            t.Fatalf(`MultyUsage: 'SRC' is %s, expected '/tmp/tmp.file.src'`, config.ArgSRC.Get())
        }

        if config.ArgDST.IsSet() != true {
            t.Fatalf(`MultyUsage: 'DST' expected to be set`)
        }
        if config.ArgDST.Get() != `/tmp/tmp.file.dst` {
            t.Fatalf(`MultyUsage: 'DST' is %s, expected '/tmp/tmp.file.dst'`, config.ArgDST.Get())
        }
    }
}
