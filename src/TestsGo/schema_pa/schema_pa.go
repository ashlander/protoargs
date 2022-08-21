package schema_pa

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
    /// String param option with default value. Note: this comment will be taken as description
    ArgparamA StringValue
    /// Integer param with default value
    ArgparamB Uint32Value
    /// Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway
    ArgparamC Int32Value
    /// Float param without default value
    ArgparamD Float32Value
    /// String param which should be anyway
    ArgparamE StringValue
    /// Integer param which may encounter multiple times
    ArgparamF ArrayInt32Flags
    /// Positional integer param, positional param is always \"required\"
    ArgPARAMG Uint64Value
    /// Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false
    ArgP_A_R_A_M_G_2 BoolValue
    /// Boolean arg with default value (despite it is declared after positional args, that is not a problem)
    Argparam_I BoolValue
    /// Boolean arg without default value
    Argparam_J BoolValue
    /// Positional float param
    ArgPARAM_FLOAT Float32Value
    /// Positional double param
    ArgPARAM_DOUBLE Float64Value
    /// Positional repeating string params, there may be only one repeating positional param
    ArgPARAMH ArrayStringFlags
    /// Print help and exit
    ArgprintHelp BoolValue
    /// Float param
    ArgparamFloat Float32Value
    /// Double param
    ArgparamDouble Float64Value

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
    config.ArgparamA = StringValue{`// tricky default value`, false}
    config.ArgparamB = Uint32Value{10, false}
    config.ArgparamC = Int32Value{0, false}
    config.ArgparamD = Float32Value{0, false}
    config.ArgparamE = StringValue{``, false}
    config.ArgPARAMG = Uint64Value{0, false}
    config.ArgP_A_R_A_M_G_2 = BoolValue{false, false}
    config.Argparam_I = BoolValue{true, false}
    config.Argparam_J = BoolValue{false, false}
    config.ArgPARAM_FLOAT = Float32Value{0, false}
    config.ArgPARAM_DOUBLE = Float64Value{0, false}
    config.ArgprintHelp = BoolValue{false, false}
    config.ArgparamFloat = Float32Value{0, false}
    config.ArgparamDouble = Float64Value{0, false}

    flags.Var(&config.ArgparamA, `a`, `String param option with default value. Note: this comment will be taken as description {OPTIONAL,type:string,default:"// tricky default value"}`)
    flags.Var(&config.ArgparamA, `a-long-param`, `String param option with default value. Note: this comment will be taken as description {OPTIONAL,type:string,default:"// tricky default value"}`)
    flags.Var(&config.ArgparamB, `b-long-param`, `Integer param with default value {OPTIONAL,type:uint32,default:10}`)
    flags.Var(&config.ArgparamC, `c`, `Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway {OPTIONAL,type:int32,default:0}`)
    flags.Var(&config.ArgparamC, `c-long-param`, `Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway {OPTIONAL,type:int32,default:0}`)
    flags.Var(&config.ArgparamD, `d-long-param`, `Float param without default value {OPTIONAL,type:float,default:0}`)
    flags.Var(&config.ArgparamE, `e`, `String param which should be anyway {REQUIRED,type:string}`)
    flags.Var(&config.ArgparamF, `f`, `Integer param which may encounter multiple times {REPEATED,type:int32}`)
    flags.BoolVar(&config.Argparam_I.Val, `i`, true, `Boolean arg with default value (despite it is declared after positional args, that is not a problem) {OPTIONAL,type:bool,default:true}`)
    flags.BoolVar(&config.Argparam_J.Val, `j-long`, false, `Boolean arg without default value {OPTIONAL,type:bool,default:false}`)
    flags.BoolVar(&config.ArgprintHelp.Val, `h`, false, `Print help and exit {OPTIONAL,type:bool,default:false}`)
    flags.BoolVar(&config.ArgprintHelp.Val, `help`, false, `Print help and exit {OPTIONAL,type:bool,default:false}`)
    flags.Var(&config.ArgparamFloat, `k`, `Float param {OPTIONAL,type:float,default:0}`)
    flags.Var(&config.ArgparamDouble, `l`, `Double param {OPTIONAL,type:double,default:0}`)

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
    block := "\n" + `usage: ` + program + ` -e paramE [-a|--a-long-param paramA] [--b-long-param paramB] [-c|--c-long-param paramC] [--d-long-param paramD] [-f paramF [-f paramF ...]] [-i] [--j-long] [-h|--help] [-k paramFloat] [-l paramDouble] PARAMG P_A_R_A_M_G_2 PARAM_FLOAT PARAM_DOUBLE PARAMH [PARAMH ...]`
    usage := splitShortUsage(block, limit)

    usage += "\n\n"
    usage += description
    usage += "\n\n" + `required arguments:`
    block = `
  -e paramE              String param which should be anyway {REQUIRED,type:string})`
    usage += splitUsage(block, limit)
    usage += "\n\n" + `required positional arguments:`
    block = `
  PARAMG                 Positional integer param, positional param is always \"required\" {REQUIRED,type:uint64})
  P_A_R_A_M_G_2          Positional boolean param, positional param is always \"required\", Note: param set - true, missing - false {REQUIRED,type:bool})
  PARAM_FLOAT            Positional float param {REQUIRED,type:float})
  PARAM_DOUBLE           Positional double param {REQUIRED,type:double})
  PARAMH                 Positional repeating string params, there may be only one repeating positional param {REQUIRED,type:string})`
    usage += splitUsage(block, limit)
    usage += "\n\n" + `optional arguments:`
    block = `
  -a, --a-long-param paramA
                         String param option with default value. Note: this comment will be taken as description {OPTIONAL,type:string,default:"// tricky default value"})
  --b-long-param paramB  Integer param with default value {OPTIONAL,type:uint32,default:10})
  -c, --c-long-param paramC
                         Integer param without default value. Avoid new lines they are rendered not correctly in help. Words will be transfered to new line anyway {OPTIONAL,type:int32,default:0})
  --d-long-param paramD  Float param without default value {OPTIONAL,type:float,default:0})
  -f paramF              Integer param which may encounter multiple times {REPEATED,type:int32})
  -i                     Boolean arg with default value (despite it is declared after positional args, that is not a problem) {OPTIONAL,type:bool,default:true})
  --j-long               Boolean arg without default value {OPTIONAL,type:bool,default:false})
  -h, --help             Print help and exit {OPTIONAL,type:bool,default:false})
  -k paramFloat          Float param {OPTIONAL,type:float,default:0})
  -l paramDouble         Double param {OPTIONAL,type:double,default:0})`
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

    if !allow_incomplete && !config.ArgparamE.IsSet() {
        errArgparamE := errors.New(`Required 'paramE' is missing`)
        fmt.Println(errArgparamE)
        fmt.Println(Usage(program, description))
        return config, errArgparamE
    }
    if !allow_incomplete && flags.NArg() < 1 {
        errArgPARAMG := errors.New(`Required positional 'PARAMG' is missing`)
        fmt.Println(errArgPARAMG)
        fmt.Println(Usage(program, description))
        return config, errArgPARAMG
    }
    errArgPARAMG := config.ArgPARAMG.Set(flags.Arg(0))
    if !allow_incomplete && errArgPARAMG != nil {
        fmt.Println(errArgPARAMG)
        fmt.Println(Usage(program, description))
        return config, errArgPARAMG
    }
    if !allow_incomplete && flags.NArg() < 2 {
        errArgP_A_R_A_M_G_2 := errors.New(`Required positional 'P-A-R-A-M-G-2' is missing`)
        fmt.Println(errArgP_A_R_A_M_G_2)
        fmt.Println(Usage(program, description))
        return config, errArgP_A_R_A_M_G_2
    }
    errArgP_A_R_A_M_G_2 := config.ArgP_A_R_A_M_G_2.Set(flags.Arg(1))
    if !allow_incomplete && errArgP_A_R_A_M_G_2 != nil {
        fmt.Println(errArgP_A_R_A_M_G_2)
        fmt.Println(Usage(program, description))
        return config, errArgP_A_R_A_M_G_2
    }
    config.Argparam_I.Present = isFlagPassed(flags, `i`)
    config.Argparam_J.Present = isFlagPassed(flags, `j-long`)
    if !allow_incomplete && flags.NArg() < 3 {
        errArgPARAM_FLOAT := errors.New(`Required positional 'PARAM-FLOAT' is missing`)
        fmt.Println(errArgPARAM_FLOAT)
        fmt.Println(Usage(program, description))
        return config, errArgPARAM_FLOAT
    }
    errArgPARAM_FLOAT := config.ArgPARAM_FLOAT.Set(flags.Arg(2))
    if !allow_incomplete && errArgPARAM_FLOAT != nil {
        fmt.Println(errArgPARAM_FLOAT)
        fmt.Println(Usage(program, description))
        return config, errArgPARAM_FLOAT
    }
    if !allow_incomplete && flags.NArg() < 4 {
        errArgPARAM_DOUBLE := errors.New(`Required positional 'PARAM-DOUBLE' is missing`)
        fmt.Println(errArgPARAM_DOUBLE)
        fmt.Println(Usage(program, description))
        return config, errArgPARAM_DOUBLE
    }
    errArgPARAM_DOUBLE := config.ArgPARAM_DOUBLE.Set(flags.Arg(3))
    if !allow_incomplete && errArgPARAM_DOUBLE != nil {
        fmt.Println(errArgPARAM_DOUBLE)
        fmt.Println(Usage(program, description))
        return config, errArgPARAM_DOUBLE
    }
    if !allow_incomplete && flags.NArg() < 5 {
        errArgPARAMH := errors.New(`Required at least one positional 'PARAMH'`)
        fmt.Println(errArgPARAMH)
        fmt.Println(Usage(program, description))
        return config, errArgPARAMH
    }
    for i := 4; i < flags.NArg(); i++ {
        errArgPARAMH := config.ArgPARAMH.Set(flags.Arg(i))
        if !allow_incomplete && errArgPARAMH != nil {
            fmt.Println(errArgPARAMH)
            fmt.Println(Usage(program, description))
            return config, errArgPARAMH
        }
    }
    config.ArgprintHelp.Present = isFlagPassed(flags, `h`)

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
