import os
import unittest
import multy_command_pa
import multy_command_create_pa
import multy_command_copy_pa

class TestMulty(unittest.TestCase):
    program = "test_multy"
    description = r"""Program description
    and another line of description
    and biiiggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg line of description
    well, and another one with extra junk
"""
    os.environ['COLUMNS']="80" # make default limit in 80 columns

    def test_command_usage(self):
        argv = [ "-h" ]
        error = False
        try:
            config = multy_command_pa.parse(self.program, self.description, argv)
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_command_create_usage(self):
        argv = [ "create", "-h" ]
        config = multy_command_pa.parse(self.program, self.description, argv[:1])
        self.assertTrue(config)
        self.assertEqual(config.COMMAND, "create")

        error = False
        try:
            config = multy_command_create_pa.parse(self.program, self.description, argv[1:])
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_positive_create(self):
        argv = [
            "create", \
            "-s", "2048", \
            "/tmp/tmp with spaces.file"
        ]

        config = multy_command_pa.parse(self.program, self.description, argv[:1])
        self.assertTrue(config)
        self.assertEqual(config.COMMAND, "create")

        config = multy_command_create_pa.parse(self.program, self.description, argv[1:])
        self.assertTrue(config)
        self.assertEqual(config.size, 2048)
        self.assertEqual(config.PATH, "/tmp/tmp with spaces.file")

    def test_command_copy_usage(self):
        argv = [ "copy", "-h" ]
        config = multy_command_pa.parse(self.program, self.description, argv[:1])
        self.assertTrue(config)
        self.assertEqual(config.COMMAND, "copy")

        error = False
        try:
            config = multy_command_copy_pa.parse(self.program, self.description, argv[1:])
        except:
            # help end program immediately
            error = True

        self.assertTrue(error)

    def test_positive_copy(self):
        argv = [
            "copy", \
            "-r", \
            "/tmp/tmp 0.file.src", \
            "/tmp/tmp 1.file.dst"
        ]

        config = multy_command_pa.parse(self.program, self.description, argv[:1])
        self.assertTrue(config)
        self.assertEqual(config.COMMAND, "copy")

        config = multy_command_copy_pa.parse(self.program, self.description, argv[1:])
        self.assertTrue(config)
        self.assertTrue(config.recursive)
        self.assertEqual(config.SRC, "/tmp/tmp 0.file.src")
        self.assertEqual(config.DST, "/tmp/tmp 1.file.dst")

if __name__ == '__main__':
    unittest.main()
