package multy_command_copy_pa

import (
    "os"
    "flag"
    "fmt"
    "errors"
    "strconv"
    "regexp"
    "strings"
)


/// Configuration structure to hold all parsed arguments as string typed entities
type Config struct {
    /// Print help and exit
    Arghelp BoolValue
    /// Recursive copy
    Argrecursive BoolValue
    /// Path to source path
    ArgSRC StringValue
    /// Path to destination path
    ArgDST StringValue

}

/// Options preparation
///
/// # Arguments
///
/// * `program` - Program name to display in help message
///
/// returns FlagSet instance ready to do parsing and configuration structure which memory is used
func PrepareOptions(program string) (*flag.FlagSet, *Config) {
    flags := flag.NewFlagSet(program, flag.ContinueOnError)

    config := new(Config)
    config.Arghelp = BoolValue{false, false}
    config.Argrecursive = BoolValue{false, false}
    config.ArgSRC = StringValue{``, false}
    config.ArgDST = StringValue{``, false}

    flags.BoolVar(&config.Arghelp.Val, `h`, false, `Print help and exit {OPTIONAL,type:bool,default:false}`)
    flags.BoolVar(&config.Arghelp.Val, `help`, false, `Print help and exit {OPTIONAL,type:bool,default:false}`)
    flags.BoolVar(&config.Argrecursive.Val, `r`, false, `Recursive copy {OPTIONAL,type:bool,default:false}`)
    flags.BoolVar(&config.Argrecursive.Val, `recursive`, false, `Recursive copy {OPTIONAL,type:bool,default:false}`)

    return flags, config
}

/// Get usage string
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `description` - Description to display in help message
///
/// returns String with usage information
func Usage(program string, description string) string {

    var limit uint32 = 80
    block := "\n" + `usage: ` + program + ` [-h|--help] [-r|--recursive] SRC DST`
    usage := splitShortUsage(block, limit)

    usage += "\n\n"
    usage += description
    usage += "\n\n" + `required positional arguments:`
    block = `
  SRC                    Path to source path {REQUIRED,type:string})
  DST                    Path to destination path {REQUIRED,type:string})`
    usage += splitUsage(block, limit)
    usage += "\n\n" + `optional arguments:`
    block = `
  -h, --help             Print help and exit {OPTIONAL,type:bool,default:false})
  -r, --recursive        Recursive copy {OPTIONAL,type:bool,default:false})`
    usage += splitUsage(block, limit)
    usage += "\n" 

    return usage
}

func splitShortUsage(usage string, limit uint32) string {
    rule := regexp.MustCompile(`\ `)
    tokens := rule.Split(usage, -1)
    return split(tokens, 25, limit)
}

func splitUsage(usage string, limit uint32) string {
    rule := regexp.MustCompile(`\ `)
    tokens := rule.Split(usage, -1)
    return split(tokens, 25, limit)
}

func split(tokens []string, shift uint32, limit uint32) string {
    // calculate shift space
    space := ""
    for i := uint32(0); i < shift; i++ {
        space += " "
    }

    result := ""
    line := ""
    for _, token := range tokens {
        if len(line) > 0 && uint32(len(line) + len(token)) > (limit-1) { // -1 for delimiter
            // push line preserving token as new line
            result += line
            if len(token) > 0 && token[0] != '-' {
                line = "\n" + space + token
            } else {
                line = " " + token
            }
        } else if len(line) > 0 && line[len(line)-1] == '\n' {
            // row finish found
            result += line
            line = " " + token
        } else {
            // append token to line via space
            if len(line) > 0 {
                line += " "
            }
            line += token // strings.TrimRight(token)
        }

        if uint32(len(line)) > limit {
            // split line by limit, the rest is pushed into next line
            var length uint32 = 0
            start := 0
            for i := range line {
                if length == limit {
                    if start > 0 {
                        result += "\n" + space
                    }
                    result += line[start:i]
                    length = 0
                    start = i
                }
                length++
            }
            if strings.TrimRight(line[start:], " ") != "" {
                line = space + line[start:] + "\n "
            } else {
                line = " "
            }
        }
    }
    result += line
    return result
}

/// Parse command line arguments, and return filled configuration
/// Simple and straight forward, thus recommended
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `description` - Description to display in help message
///
/// returns Result with configuration structure, or error message
func Parse(program string, description string, allow_incomplete bool) (*Config, error) {
    return ParseExt(program, os.Args, description, allow_incomplete)
}

/// Parse command line arguments, and return filled configuration
///
/// # Arguments
///
/// * `program` - Program name to display in help message
/// * `args` - Command line arguments as str slice
/// * `description` - Description to display in help message
/// * `allow_incomplete` - Allow partial parsing ignoring missing required arguments
/// wrong type cast will produce error anyway
///
/// returns Result with configuration structure, or error message
func ParseExt(program string, args []string, description string, allow_incomplete bool) (*Config, error) {
    flags, config := PrepareOptions(program)

    usage := Usage(program, description)
    flags.Usage = func() {
        fmt.Printf("%s", usage)
    }

    err := flags.Parse(args[1:])
    if err != nil {
        return config, err
    }

    config.Arghelp.Present = isFlagPassed(flags, `h`)
    config.Argrecursive.Present = isFlagPassed(flags, `r`)
    if !allow_incomplete && flags.NArg() < 1 {
        errArgSRC := errors.New(`Required positional 'SRC' is missing`)
        fmt.Println(errArgSRC)
        fmt.Println(Usage(program, description))
        return config, errArgSRC
    }
    errArgSRC := config.ArgSRC.Set(flags.Arg(0))
    if !allow_incomplete && errArgSRC != nil {
        fmt.Println(errArgSRC)
        fmt.Println(Usage(program, description))
        return config, errArgSRC
    }
    if !allow_incomplete && flags.NArg() < 2 {
        errArgDST := errors.New(`Required positional 'DST' is missing`)
        fmt.Println(errArgDST)
        fmt.Println(Usage(program, description))
        return config, errArgDST
    }
    errArgDST := config.ArgDST.Set(flags.Arg(1))
    if !allow_incomplete && errArgDST != nil {
        fmt.Println(errArgDST)
        fmt.Println(Usage(program, description))
        return config, errArgDST
    }

    return config, nil
}

func isFlagPassed(flags *flag.FlagSet, name string) bool {
    found := false
    flags.Visit(func(f *flag.Flag) {
        if f.Name == name {
            found = true
        }
    })
    return found
}

type (
    StringValue struct { // A string value for StringOption interface.
        Val string // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option StringValue) Get() string { return option.Val }
func (option StringValue) IsSet() bool { return option.Present }

func (i *StringValue) String() string {
    return fmt.Sprint( string(i.Get()) )
}

func (i *StringValue) Set(value string) error {
    var err error = nil
    typedValue := value
    *i = StringValue{string(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayStringFlags []string

func (a *ArrayStringFlags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayStringFlags) Set(value string) error {
    var err error = nil
    typedValue := value
    *i = append(*i, string(typedValue))
    return err
}

type (
    BoolValue struct { // A bool value for BoolOption interface.
        Val bool // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option BoolValue) Get() bool { return option.Val }
func (option BoolValue) IsSet() bool { return option.Present }

func (i *BoolValue) String() string {
    return fmt.Sprint( bool(i.Get()) )
}

func (i *BoolValue) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseBool(value)
    *i = BoolValue{bool(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayBoolFlags []bool

func (a *ArrayBoolFlags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayBoolFlags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseBool(value)
    *i = append(*i, bool(typedValue))
    return err
}

type (
    Int32Value struct { // A int32 value for Int32Option interface.
        Val int32 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Int32Value) Get() int32 { return option.Val }
func (option Int32Value) IsSet() bool { return option.Present }

func (i *Int32Value) String() string {
    return fmt.Sprint( int32(i.Get()) )
}

func (i *Int32Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseInt(value, 10, 32)
    *i = Int32Value{int32(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayInt32Flags []int32

func (a *ArrayInt32Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayInt32Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseInt(value, 10, 32)
    *i = append(*i, int32(typedValue))
    return err
}

type (
    Uint32Value struct { // A uint32 value for Uint32Option interface.
        Val uint32 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Uint32Value) Get() uint32 { return option.Val }
func (option Uint32Value) IsSet() bool { return option.Present }

func (i *Uint32Value) String() string {
    return fmt.Sprint( uint32(i.Get()) )
}

func (i *Uint32Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseUint(value, 10, 32)
    *i = Uint32Value{uint32(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayUint32Flags []uint32

func (a *ArrayUint32Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayUint32Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseUint(value, 10, 32)
    *i = append(*i, uint32(typedValue))
    return err
}

type (
    Int64Value struct { // A int64 value for Int64Option interface.
        Val int64 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Int64Value) Get() int64 { return option.Val }
func (option Int64Value) IsSet() bool { return option.Present }

func (i *Int64Value) String() string {
    return fmt.Sprint( int64(i.Get()) )
}

func (i *Int64Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseInt(value, 10, 64)
    *i = Int64Value{int64(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayInt64Flags []int64

func (a *ArrayInt64Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayInt64Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseInt(value, 10, 64)
    *i = append(*i, int64(typedValue))
    return err
}

type (
    Uint64Value struct { // A uint64 value for Uint64Option interface.
        Val uint64 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Uint64Value) Get() uint64 { return option.Val }
func (option Uint64Value) IsSet() bool { return option.Present }

func (i *Uint64Value) String() string {
    return fmt.Sprint( uint64(i.Get()) )
}

func (i *Uint64Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseUint(value, 10, 64)
    *i = Uint64Value{uint64(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayUint64Flags []uint64

func (a *ArrayUint64Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayUint64Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseUint(value, 10, 64)
    *i = append(*i, uint64(typedValue))
    return err
}

type (
    Float32Value struct { // A float32 value for Float32Option interface.
        Val float32 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Float32Value) Get() float32 { return option.Val }
func (option Float32Value) IsSet() bool { return option.Present }

func (i *Float32Value) String() string {
    return fmt.Sprint( float32(i.Get()) )
}

func (i *Float32Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseFloat(value, 32)
    *i = Float32Value{float32(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayFloat32Flags []float32

func (a *ArrayFloat32Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayFloat32Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseFloat(value, 32)
    *i = append(*i, float32(typedValue))
    return err
}

type (
    Float64Value struct { // A float64 value for Float64Option interface.
        Val float64 // possible default value
        Present bool // is true - flag showing argument was present in command line
    }
)

func (option Float64Value) Get() float64 { return option.Val }
func (option Float64Value) IsSet() bool { return option.Present }

func (i *Float64Value) String() string {
    return fmt.Sprint( float64(i.Get()) )
}

func (i *Float64Value) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseFloat(value, 64)
    *i = Float64Value{float64(typedValue), true}
    return err
}

// Array wrapper to gather repeated arguments
type ArrayFloat64Flags []float64

func (a *ArrayFloat64Flags) String() string {
    var s string = "{ "
    for i := 0; i < len(*a); i++ {
        s += fmt.Sprint((*a)[i]," ")
    }
    if len(s) > 0 {
        s = s[:len(s)-1]
    }
    s+=" }"
    return s
}

func (i *ArrayFloat64Flags) Set(value string) error {
    var err error = nil
    typedValue, err := strconv.ParseFloat(value, 64)
    *i = append(*i, float64(typedValue))
    return err
}
