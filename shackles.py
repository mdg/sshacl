#! /usr/bin/env python

from sys import stdin, stdout
import subprocess
import yaml
import argparse


class ArgumentFormatError(Exception):
    "Error for when a command argument can't be correctly formatted"
    def __init__(self, arg):
        "Pass the argument that failed formatting"
        Exception.__init__(self, "Cannot format '%s'" % arg)
        self.arg = arg

class Command(object):
    "An object to store information about a command that can be called"
    def __init__(self, name, args=None, help_text=None):
        """Construct the command

        @name       the name of the command to be run
        @args       list of arguments to be passed to the command
                    can be templated
        @help_text  description of what the command does; to be reported
                    to clients
        """
        self._name = name
        if args is None:
            args = []
        self._args = args
        self._help_text = help_text

    def name(self):
        "Return te name of this command"
        return self._name

    def command(self, **kwargs):
        """Convert the object into an array that can be executed

        Format any arguments with kwargs as input to the argument template"""
        if not kwargs:
            kwargs = {}

        cmd = [self._name]
        for arg in self._args:
            try:
                cmd.append(arg % kwargs)
            except ValueError, x:
                raise ArgumentFormatError(arg)
        return cmd

    def __repr__(self):
        return "<Command %s>" % (self._name)


class CommandLibrary(object):
    """The set of commands that can be run on this system."""
    def __init__(self):
        self._commands = dict()

    def add(self, name, command, args=None, help_text=None):
        """Add a command to the library"""
        if args is None:
            args = []
        if help_text is None:
            help_text = str()

        self._commands[name] = Command(command, args, help_text)

    def __getitem__(self, name):
        "Lookup any command based on its name"
        return self._commands[name]

    def command(self, name, **kwargs):
        "Find the command and convert it with the kwargs"
        cmd = self._commands[name]
        return cmd.command(**kwargs)

    def __repr__(self):
        return "<CommandLibrary %s>" % repr(self._commands.values())

def construct_library(lib_data):
    '''Process YAML-loaded data into a library of command objects'''
    lib = CommandLibrary()
    for name, item in lib_data.iteritems():
        cmd = item['cmd']

        args = None
        if 'args' in item:
            args = item['args']
        elif 'arg' in item:
            args = [ item['arg'] ]

        help_text = None
        if 'help' in item:
            help_text = item['help']

        lib.add(name, cmd, args, help_text)
    return lib


def shell_exec(cmd, args, output_stream):
    """Execute a shackle command with the given arguments"""
    full_command = cmd.command(**args)
    subprocess.call(full_command)
    return 0

def create_noop_exec(result=0):
    """Create an executor function that only simulates executing a call

    Can set the result explicitly upon creation"""
    def f(cmd, args, output_stream):
        full_command = cmd.command(**args)
        output_stream.write("Execute %s\n" % str(full_command))
        return result
    return f

def run_shell(lib, executor, input_data, output_stream):
    """Run the shell given the library, executor & input data

    Write the output to the output_stream"""
    args = dict()
    if 'args' in input_data:
        args = input_data['args']

    if 'help' in input_data:
        output_stream.write(input_data['help'])
        result = 0
    elif 'exec' in input_data:
        command_name = input_data['exec']
        result = executor(lib[command_name], args, output_stream)
    return result


def argument_parser():
    "Construct the argument parser for the command line"
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--library'
            , default='~/.shackles.yaml'
            , help='the library of potential actions that can be executed '
            '(default=~/.shackles.yaml)')
    args.add_argument('-c', '--command'
            , help="the command file to be executed (default=stdin)")
    args.add_argument('-n', '--dry-run', dest='noop'
            , action='store_true', default=False
            , help="simulate what will be executed")
    return args


def main():
    args = argument_parser()
    opts = args.parse_args()

    with open(opts.library) as lib_file:
        lib_data = yaml.safe_load(lib_file)
    library = construct_library(lib_data)

    if opts.command:
        with open(opts.command) as cmd_file:
            cmd_data = yaml.safe_load(cmd_file)
    else:
        cmd_data = yaml.safe_load(stdin)

    # Set the executor
    executor = shell_exec
    if opts.noop:
        # Override the executor if noop option is specified
        executor = create_noop_exec()

    return run_shell(library, executor, cmd_data, stdout)

if __name__ == "__main__":
    exit(main())
