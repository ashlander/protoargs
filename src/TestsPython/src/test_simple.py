import os
import unittest
import simple_pa

class TestSimpleSchema(unittest.TestCase):
    program = "test_simple"
    description = r"""Program description
    and another line of description
    and biiiggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg line of description
    well, and another one with extra junk
"""
    os.environ['COLUMNS']="80" # make default limit in 80 columns

    def test_usage(self):
        argv = [ "-h" ]
        error = False
        try:
            config = simple_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_all_positive_spaces(self):
        argv = [
            "--count", "2", \
            "--configuration", "/tmp/conf", \
            "--flags", "true", \
            "--flags", "false", \
            "-c", "flags should be true and false", \
            "--o-underscore", "no underscore", \
            "--r-underscore", "no underscore", \
            "--a-underscore", "no underscore0", \
            "--a-underscore", "no underscore1",
        ]
        config = simple_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertEqual(config.count, 2)
        self.assertEqual(config.configuration, "/tmp/conf")
        self.assertEqual(config.flags, [True, False])
        self.assertEqual(config.c, "flags should be true and false")
        self.assertEqual(config.o_underscore, "no underscore")
        self.assertEqual(config.r_underscore, "no underscore")
        self.assertEqual(config.a_underscore, [ "no underscore0", "no underscore1" ])

    def test_all_positive_equals(self):
        argv = [
            r"""--count=2""", \
            r"""--configuration=/tmp/conf""", \
            r"""--flags=true""", \
            r"""--flags=false""", \
            r"""-c=flags should be true and false""", \
            r"""--o-underscore=no underscore""", \
            r"""--r-underscore=no underscore""", \
            r"""--a-underscore=no underscore0""", \
            r"""--a-underscore=no underscore1""",
        ]
        config = simple_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertEqual(config.count, 2)
        self.assertEqual(config.configuration, "/tmp/conf")
        self.assertEqual(config.flags, [True, False])
        self.assertEqual(config.c, "flags should be true and false")
        self.assertEqual(config.o_underscore, "no underscore")
        self.assertEqual(config.r_underscore, "no underscore")
        self.assertEqual(config.a_underscore, [ "no underscore0", "no underscore1" ])

    def test_check_wrong_positional(self):
        argv = [
            "--count", "1", \
            "--configuration", "/tmp/conf", \
            "--flags", "true", \
            "--flags", "false", \
            "-c", "flags should be true and false", \
            "--r-underscore", "no underscore", \
            "positional_value", \
            "positional_value", \
            "positional_value", \
            "positional_value", \
            "positional_value", \
        ]

        error = False
        try:
            config = simple_pa.parse(self.program, self.description, argv)
        except:
            # extra unknown args considered an error
            error = True
        self.assertTrue(error)

    def test_check_wrong_type(self):
        argv = [
            "--count", "stringnotdigit", \
            "--configuration", "/tmp/conf", \
            "--flags", "true", \
            "--flags", "false", \
            "-c", "flags should be true and false", \
            "--r-underscore", "no underscore", \
        ]

        error = False
        try:
            config = simple_pa.parse(self.program, self.description, argv)
        except:
            # extra unknown args considered an error
            error = True
        self.assertTrue(error)

    def test_allow_incomplete_wrong_type(self):
        argv = [
            "--count", "stringnotdigit", \
            "--configuration", "/tmp/conf", \
            "--flags", "true", \
            "--flags", "false", \
            "-c", "flags should be true and false", \
            "--r-underscore", "no underscore", \
        ]

        error = False
        try:
            config = simple_pa.parse(self.program, self.description, argv, allowIncomplete=True)
        except:
            # type check is still done
            error = True
        self.assertTrue(error)


if __name__ == '__main__':
    unittest.main()
