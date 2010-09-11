from shackles import *
import yaml
import unittest
from StringIO import StringIO


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
        'Test how a command handles an argument w/ a bad format string'
        cmd = Command('cp', ['%(src)s', '%(dest)'])
        args = {'src':'file1', 'dest':'file2'}
        try:
            cmd.command(**args)
            self.fail("No exception was thrown")
        except ArgumentFormatError, afe:
            self.assertEqual("Cannot format '%(dest)'", str(afe))
            self.assertEqual("%(dest)", afe.arg)


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


class NoopExecTest(unittest.TestCase):
    'Test behavior of the noop executor class'

    def test_noop_exec_args(self):
        'Test how noop_exec handles basic execution case'
        cmd = Command('cp', ['%(src)s', '%(dest)s'])
        args = {'src':'file1', 'dest':'file2'}
        output = StringIO()
        executor = create_noop_exec()
        result = executor(cmd, args, output)
        self.assertEqual("Execute ['cp', 'file1', 'file2']\n"
                , output.getvalue())
        self.assertEqual(0, result)


class RunShellTest(unittest.TestCase):
    'Test the behavior of the run_shell function'

    def test_run_shell(self):
        lib = construct_library(yaml.load(TEST_CMD_YAML))
        call_data = {'exec':'test2'}
        output = StringIO()
        result = run_shell(lib, create_noop_exec(), call_data, output)

        self.assertEqual(0, result)
        self.assertEqual("Execute ['pwd']\n", output.getvalue())
