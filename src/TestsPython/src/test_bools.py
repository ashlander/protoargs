import os
import unittest
import bools_pa

class TestBoolsSchema(unittest.TestCase):
    program = "test_bools"
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
            config = bools_pa.parse(self.program, self.description, argv)
        except:
            # help ends program immediately
            error = True

        self.assertTrue(error)

    def test_long_and_short_args_together(self):
        argv = [
            "--rb", \
            "--reqbool", \
            "false", \
            "true", \
            "true", "false", "true"
        ]
        config = bools_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertTrue(config.req_bool)

    def test_positive_short(self):
        argv = [
            "--rb", \
            "False", \
            "True", \
            "True", "False", "True"
        ]
        config = bools_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertTrue(config.req_bool)
        self.assertTrue(config.opt_bool) # default value is True
        self.assertFalse(config.rep_bool)
        self.assertFalse(config.OPTBOOL)
        self.assertTrue(config.ALTBOOL)
        self.assertTrue(config.REOBOOL, [ True, False, True ])

    def test_positive_all(self):
        argv = [
            "--rb", \
            "--optbool", "False", \
            "--repbool", "False", \
            "--repbool", "True", \
            "--repbool", "False", \
            "False", \
            "True", \
            "True", "False", "True"
        ]
        config = bools_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertTrue(config.req_bool)
        self.assertFalse(config.opt_bool)
        self.assertEqual(config.rep_bool, [ False, True, False ])
        self.assertFalse(config.OPTBOOL)
        self.assertTrue(config.ALTBOOL)
        self.assertTrue(config.REOBOOL, [ True, False, True ])

    def test_positive_required(self):
        argv = [
            "--reqbool", \
            "True", "False", "True"
        ]
        config = bools_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

    def test_positional_wrong_type(self):
        argv = [
            "--reqbool", \
            "True", "False", "True", "23"
        ]
        try:
            config = bools_pa.parse(self.program, self.description, argv)
        except:
            error = True

        self.assertTrue(error)

if __name__ == '__main__':
    unittest.main()
