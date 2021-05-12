import sys
import multy_command_pa
import multy_command_create_pa
import multy_command_copy_pa

class ArgsParser:

    def parseCommand(self, argv):
        self.config = multy_command_pa.parse("program", "Useful multi command", argv)

    def parseCreate(self, argv):
        self.config = multy_command_create_pa.parse("program create", "Useful create", argv)

    def parseCopy(self, argv):
        self.config = multy_command_copy_pa.parse("program copy", "Useful copy", argv)

if __name__ == "__main__":
    parser = ArgsParser()

    parser.parseCommand(sys.argv[1:2])
    print(parser.config)

    if (parser.config.COMMAND == "create"):
        parser.parseCreate(sys.argv[2:])
    elif (parser.config.COMMAND == "copy"):
        parser.parseCopy(sys.argv[2:])
    else:
        sys.exit(1)
    print(parser.config)
