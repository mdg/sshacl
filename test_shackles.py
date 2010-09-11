from shackles import *
import yaml
import unittest


class CommandTest(unittest.TestCase):
    """Test the Command class"""

    def testNoParams(self):
        "Test Command object created with no params"
        cmd = Command("cat")
        self.assertEqual("cat", cmd.name())
        self.assertEqual(["cat"], cmd.command())
 
    def testOneStaticParam(self):
        "Test Command object when created with 1 static param"
        cmd = Command("cat", args=["/super/file"])
        self.assertEqual("cat", cmd.name())
        self.assertEqual(["cat", "/super/file"], cmd.command())

    def testOneDynamicParam(self):
        "test Command object when created with dynamic params"
        cmd = Command("yum", args=["install", "%(rpm)s"])
        self.assertEqual("yum", cmd.name())
        self.assertEqual(["yum", "install", "git"], cmd.command(rpm='git'))

    def test_incomplete_format(self):
        cmd = Command('cp', ['%(src)s', '%(dest)'])
        args = {'src':'file1', 'dest':'file2'}
        try:
            cmd.command(**args)
            self.fail("No exception was thrown")
        except ArgumentFormatError, afe:
            self.assertEqual("Cannot format '%(dest)'", str(afe))


TEST_CMD_YAML = """
test1:
    cmd: ls
    desc: Check for matching files.
    arg: "${match}"
test2:
    cmd: pwd
    desc: Check the present directory.
test3:
    cmd: ls
    desc: Check the present directory.
    args:
      - --color
      - "${color}"
"""

class CommandLibraryTest(unittest.TestCase):
    """Tests for the command library object."""

    def test_library_command(self):
        "Test the library properly returns a subprocess cmd."
        lib = CommandLibrary()
        lib.add('test1', "ls", args=['match','dog'])
        self.assertEqual(["ls", "match", "dog"], lib.command('test1'))


class ConstructLibraryTest(unittest.TestCase):
    """Tests for the construct library function"""

    def test_construct_library(self):
        'Test library construction'
        lib = construct_library(yaml.load(TEST_CMD_YAML))
        self.assertEqual('ls', lib['test1'].name())
        self.assertEqual('pwd', lib['test2'].name())
        self.assertEqual('ls', lib['test3'].name())


