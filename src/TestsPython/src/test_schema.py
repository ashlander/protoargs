import os
import unittest
import schema_pa

class TestSchema(unittest.TestCase):
    program = "test_schema"
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
            config = schema_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_short_and_long_args_together(self):
        argv = [
            "-e", "valueE", \
            "-a", "somevalue1", \
            "--a-long-param", "somevalue", \
            "50", \
            "true", \
            "0.5", \
            "0.7", \
            "pos1", "pos2", "pos3"
        ]
        config = schema_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        self.assertEqual(config.paramA, "somevalue")

    def test_positive_short(self):
        argv = [
            "-e", "valueE", \
            "50", \
            "false", \
            "0.5", \
            "0.7", \
            "pos1", "pos2", "pos3"
        ]
        config = schema_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        print(config)
        self.assertEqual(config.paramA, "// tricky default value") # default
        self.assertEqual(config.paramB, 10) # default
        self.assertFalse(config.paramC) # no default assigned, return None
        self.assertFalse(config.paramD) # no default assigned, return None
        self.assertEqual(config.paramE, "valueE")
        self.assertFalse(config.paramF) # no default assigned, return None
        self.assertEqual(config.param_I, True)
        self.assertFalse(config.param_J) # no default assigned, return None
        self.assertEqual(config.PARAMG, 50)
        self.assertEqual(config.P_A_R_A_M_G_2, False)
        self.assertEqual(config.PARAM_FLOAT, 0.5)
        self.assertEqual(config.PARAM_DOUBLE, 0.7)
        self.assertEqual(config.PARAMH, [ "pos1", "pos2", "pos3" ])

    def test_positive_all(self):
        argv = [
             "-e", "valueE", \
             "--a-long-param", "somevalue", \
             "--b-long-param", "4", \
             "-c", "555", \
             "--d-long-param", "555.5", \
             "-f", "1", \
             "-f", "2", \
             "-f", "3", \
             "-i", "True", \
             "--j-long", \
             "50", \
             "false", \
             "0.5", \
             "0.7", \
             "pos1", "pos2", "pos3"
        ]
        config = schema_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        print(config)
        self.assertEqual(config.paramA, "somevalue")
        self.assertEqual(config.paramB, 4)
        self.assertEqual(config.paramC, 555)
        self.assertEqual(config.paramD, 555.5)
        self.assertEqual(config.paramE, "valueE")
        self.assertEqual(config.paramF, [ 1, 2, 3 ])
        self.assertEqual(config.param_I, True)
        self.assertEqual(config.param_J, True)
        self.assertEqual(config.PARAMG, 50)
        self.assertEqual(config.P_A_R_A_M_G_2, False)
        self.assertEqual(config.PARAM_FLOAT, 0.5)
        self.assertEqual(config.PARAM_DOUBLE, 0.7)
        self.assertEqual(config.PARAMH, [ "pos1", "pos2", "pos3" ])

    def test_positive_all_equals(self):
        argv = [
             "-e=valueE", \
             "--a-long-param=somevalue", \
             "--b-long-param=4", \
             "-c=555", \
             "--d-long-param=555.5", \
             "-f=1", \
             "-f=2", \
             "-f=3", \
             "-i=True", \
             "--j-long", \
             "50", \
             "false", \
             "0.5", \
             "0.7", \
             "pos1", "pos2", "pos3"
        ]
        config = schema_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        print(config)
        self.assertEqual(config.paramA, "somevalue")
        self.assertEqual(config.paramB, 4)
        self.assertEqual(config.paramC, 555)
        self.assertEqual(config.paramD, 555.5)
        self.assertEqual(config.paramE, "valueE")
        self.assertEqual(config.paramF, [ 1, 2, 3 ])
        self.assertEqual(config.param_I, True)
        self.assertEqual(config.param_J, True)
        self.assertEqual(config.PARAMG, 50)
        self.assertEqual(config.P_A_R_A_M_G_2, False)
        self.assertEqual(config.PARAM_FLOAT, 0.5)
        self.assertEqual(config.PARAM_DOUBLE, 0.7)
        self.assertEqual(config.PARAMH, [ "pos1", "pos2", "pos3" ])

    def test_positive_all_equals_minus(self):
        argv = [
             "-e=valueE", \
             "--a-long-param=somevalue", \
             "--b-long-param=-4", \
             "-c=-555", \
             "--d-long-param=-555.5", \
             "-f=-1", \
             "-f=-2", \
             "-f=-3", \
             "-i=True", \
             "--j-long", \
             "-50", \
             "false", \
             "-0.5", \
             "-0.7", \
             "pos1", "pos2", "pos3"
        ]
        config = schema_pa.parse(self.program, self.description, argv)
        self.assertNotEqual(config, None)

        print(config)
        self.assertEqual(config.paramA, "somevalue")
        self.assertEqual(config.paramB, -4)
        self.assertEqual(config.paramC, -555)
        self.assertEqual(config.paramD, -555.5)
        self.assertEqual(config.paramE, "valueE")
        self.assertEqual(config.paramF, [ -1, -2, -3 ])
        self.assertEqual(config.param_I, True)
        self.assertEqual(config.param_J, True)
        self.assertEqual(config.PARAMG, -50)
        self.assertEqual(config.P_A_R_A_M_G_2, False)
        self.assertEqual(config.PARAM_FLOAT, -0.5)
        self.assertEqual(config.PARAM_DOUBLE, -0.7)
        self.assertEqual(config.PARAMH, [ "pos1", "pos2", "pos3" ])

    def test_missing_required(self):
        argv = [
             "50", \
             "0"
        ]
        error = False
        try:
            config = schema_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_missing_repeated_positional(self):
        argv = [
             "-e", "valueE", \
             "50", \
             "false", \
             "0.5", \
             "0.7", \
        ]
        error = False
        try:
            config = schema_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_positional_wrong_type(self):
        argv = [
            "-e", "valueE", \
            "50f", \
            "0e", \
            "0.5d", \
            "0.7d", \
            "pos1", "pos2", "pos3"
        ]
        error = False
        try:
            config = schema_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)


if __name__ == '__main__':
    unittest.main()
