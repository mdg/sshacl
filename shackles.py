#! /usr/bin/env python

from sys import stdin, stdout
import os.path
import shlex
import subprocess
import yaml
import argparse


class ArgumentFormatError(Exception):
    "Error for when an action's argument can't be correctly formatted"
    def __init__(self, arg):
        "Pass the argument that failed formatting"
        Exception.__init__(self, "Cannot format '%s'" % arg)
        self.arg = arg

class Action(object):
    "An object to store information about an action that can be called"
    def __init__(self, command_line, help_text=None):
        """Construct the action object

        @command_line  the name of the command to be run
        @help_text     description of what the action does; to be reported
                       to clients
        """
        args = shlex.split(command_line)
        self._cmd = args[0]
        self._args = args[1:]
        self._help_text = help_text

    def cmd(self):
        "Return the program that will be executed as part of this action"
        return self._cmd

    def executable(self, **kwargs):
        """Convert the action into a list that can be executed

        Format any arguments with kwargs as input to the argument template"""
        if not kwargs:
            kwargs = {}

        exe = [self._cmd]
        for arg in self._args:
            try:
                exe.append(arg % kwargs)
            except ValueError, x:
                raise ArgumentFormatError(arg)
        return exe

    def __repr__(self):
        return "<Action %s>" % (self._cmd)


class ActionLibrary(object):
    """The set of actions that can be run on this system."""
    def __init__(self):
        self._actions = dict()

    def add(self, name, command_line, help_text=None):
        """Add an action to the library
        
        @name          the name of this action
        @command_line  the command line for this action, may include templates
        @help_text     help text to be displayed to remote clients
        """
        if help_text is None:
            help_text = str()

        self._actions[name] = Action(command_line, help_text)

    def __getitem__(self, name):
        "Lookup any action based on its name"
        return self._actions[name]

    def executable(self, name, **kwargs):
        "Find the action and convert it to an executable with the kwargs"
        action = self._actions[name]
        return action.executable(**kwargs)

    def __repr__(self):
        return "<ActionLibrary %s>" % repr(self._actions.values())

def construct_library(lib_data):
    '''Process YAML-loaded data into a library of command objects'''
    lib = ActionLibrary()
    for name, item in lib_data.iteritems():
        cmd = item['cmd']

        help_text = None
        if 'help' in item:
            help_text = item['help']

        lib.add(name, cmd, help_text)

    return lib


def shell_exec(action, args, output_stream):
    """Execute a shackle action with the given arguments"""
    exe = action.executable(**args)
    subprocess.call(exe)
    return 0

def create_noop_exec(result=0):
    """Create an executor function that only simulates executing a call

    Can set the result explicitly upon creation"""
    def f(action, args, output_stream):
        exe = action.executable(**args)
        output_stream.write("Execute %s\n" % str(exe))
        return result
    return f

def run_shell(lib, executor, call_data, output_stream):
    """Run the shell given the library, executor & input data

    Write the output to the output_stream"""
    args = dict()
    if 'args' in call_data:
        args = call_data['args']

    if 'help' in call_data:
        output_stream.write(call_data['help'])
        result = 0
    elif 'exec' in call_data:
        action_name = call_data['exec']
        result = executor(lib[action_name], args, output_stream)
    return result


def argument_parser():
    "Construct the argument parser for the command line"
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--library'
            , default='~/.shackles.yaml'
            , help='the library of potential actions that can be executed '
            '(default=~/.shackles.yaml)')
    args.add_argument('-c', '--call'
            , help="the call file to be executed (default=stdin)")
    args.add_argument('-n', '--dry-run', dest='noop'
            , action='store_true', default=False
            , help="simulate what will be executed")
    return args

def die_from_missing_file(file_type, path):
    """Report a missing file error to the user and die
    
    Exit with code 1"""
    print("%s file does not exist: %s" % (file_type, path))
    exit(1)

def main():
    args = argument_parser()
    opts = args.parse_args()

    # Load the library data
    if not os.path.exists(opts.library):
        die_from_missing_file('library', opts.library)

    with open(opts.library) as lib_file:
        lib_data = yaml.safe_load(lib_file)
    library = construct_library(lib_data)

    # Load the call data
    if opts.call:
        if not os.path.exists(opts.call):
            die_from_missing_file('call', opts.call)

        with open(opts.call) as call_file:
            call_data = yaml.safe_load(call_file)
    else:
        call_data = yaml.safe_load(stdin)

    # Set the executor
    executor = shell_exec
    if opts.noop:
        # Override the executor if noop option is specified
        executor = create_noop_exec()

    return run_shell(library, executor, call_data, stdout)

if __name__ == "__main__":
    exit(main())
