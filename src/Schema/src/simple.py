import sys
import simple_pa

class ArgsParser:

    def parse(self, argv):
        self.config = simple_pa.parse("schema", 
                "Test schema", argv)

if __name__ == "__main__":
    parser = ArgsParser()
    parser.parse(sys.argv[1:])
    print(parser.config)
