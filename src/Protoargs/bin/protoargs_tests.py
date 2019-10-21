#!/usr/bin/python

import ConfigParser
from protoargs import ArgsParser, CppGenerator

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    parser = ArgsParser()
    parser.parse(sys.argv[1:])

    # [#5] TODO normal unit tests

    print "[INFO] Generate cpp code"
    generator = CppGenerator()
    generator.generate( parser.config.getProtoPath() )
