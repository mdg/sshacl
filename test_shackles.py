from shackles import *
import yaml
import unittest
from StringIO import StringIO


class ActionTest(unittest.TestCase):
    """Test the Action class"""

    def testNoParams(self):
        "Test Action object created with no params"
        action = Action("cat")
        self.assertEqual("cat", action.cmd())
        self.assertEqual(["cat"], action.executable())
 
    def testOneStaticParam(self):
        "Test Action object when created with 1 static param"
        action = Action("cat /super/file")
        self.assertEqual("cat", action.cmd())
        self.assertEqual(["cat", "/super/file"], action.executable())

    def testOneDynamicParam(self):
        "test Action object when created with dynamic params"
        action = Action("yum install %(rpm)s")
        self.assertEqual("yum", action.cmd())
        self.assertEqual(["yum", "install", "git"]
                , action.executable(rpm='git'))

    def test_incomplete_format(self):
        'Test how an action handles an argument w/ a bad format string'
        action = Action('cp %(src)s %(dest)')
        args = {'src':'file1', 'dest':'file2'}
        try:
            action.executable(**args)
            self.fail("No exception was thrown")
        except ArgumentFormatError, afe:
            self.assertEqual("Cannot format '%(dest)'", str(afe))
            self.assertEqual("%(dest)", afe.arg)

    def test_repr(self):
        'Test how an action is converted to a string'
        action = Action('cp', ['file1', 'file2'])
        self.assertEqual("<Action cp>", repr(action))


TEST_LIBRARY_YAML = """
test1:
    cmd: ls %(match)s
    help: Check for matching files.
test2:
    cmd: pwd
    help: Check the present directory.
test3:
    cmd: ls --color %(color)s
    help: Check the present directory.
cp_cmd:
    cmd: cp %(file1)s %(file2)s
    help: Copy one file to another
"""

class ActionLibraryTest(unittest.TestCase):
    """Tests for the action library object."""

    def test_library_executable(self):
        "Test the library properly returns a subprocess cmd."
        lib = ActionLibrary()
        lib.add('test1', "ls match dog")
        self.assertEqual(["ls", "match", "dog"], lib.executable('test1'))


class ConstructLibraryTest(unittest.TestCase):
    """Tests for the construct library function"""

    def test_construct_library(self):
        'Test library construction'
        lib = construct_library(yaml.load(TEST_LIBRARY_YAML))
        self.assertEqual('ls', lib['test1'].cmd())
        self.assertEqual('pwd', lib['test2'].cmd())
        self.assertEqual('ls', lib['test3'].cmd())
        self.assertEqual('cp', lib['cp_cmd'].cmd())


class NoopExecTest(unittest.TestCase):
    'Test behavior of the noop executor class'

    def test_noop_exec_args(self):
        'Test how noop_exec handles basic execution case'
        action = Action('cp %(src)s %(dest)s')
        args = {'src':'file1', 'dest':'file2'}
        output = StringIO()
        executor = create_noop_exec()
        result = executor(action.executable(**args), output)
        self.assertEqual("Execute ['cp', 'file1', 'file2']\n"
                , output.getvalue())
        self.assertEqual(0, result)


class RunShellTest(unittest.TestCase):
    'Test the behavior of the run_shell function'

    def test_run_live_shell(self):
        """Check that the shell correctly calls the live executor

        Ignores the output"""
        lib = ActionLibrary()
        lib.add('ls', 'ls')
        call_data = {'exec':'ls'}
        result = run_shell(lib, shell_exec, call_data, StringIO())
        self.assertEquals(0, result)

    def test_run_noop_shell(self):
        lib = construct_library(yaml.load(TEST_LIBRARY_YAML))
        call_data = {'exec':'test2'}
        output = StringIO()
        result = run_shell(lib, create_noop_exec(), call_data, output)

        self.assertEqual(0, result)
        self.assertEqual("Execute ['pwd']\n", output.getvalue())
