#! /usr/bin/env python

from sys import stdin, stdout
import subprocess
import yaml
import argparse


class Command(object):
    def __init__(self, name, args=None, help_text=None):
        self._name = name
        if args is None:
            args = []
        self._args = args
        self._help_text = help_text

    def name(self):
        return self._name

    def command(self, **kwargs):
        if not kwargs:
            kwargs = {}

        cmd = [self._name]
        for arg in self._args:
            cmd.append(arg % kwargs)
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
        return self._commands[name]

    def command(self, name, **kwargs):
        cmd = self._commands[name]
        return cmd.command(**kwargs)

    def __repr__(self):
        return "<CommandLibrary %s>" % repr(self._commands.values())

def construct_library(lib_data):
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


def shell_exec(cmd, args):
    """Execute a shackle command with the given arguments"""
    full_command = cmd.command(**args)
    subprocess.call(full_command)

def noop_exec(cmd, args, output_stream):
    """Simulate executing a command"""
    full_command = cmd.command(**args)
    output_stream.write("Execute %s\n" % str(full_command))

def run_shell(lib, executor, input_data, output_stream):
    args = dict()
    if 'args' in input_data:
        args = input_data['args']

    if 'help' in input_data:
        output_stream.write(input_data['help'])
        return 0
    elif 'exec' in input_data:
        command_name = input_data['exec']
        executor(lib[command_name], args, output_stream)
    return 0


def argument_parser():
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--library'
            , default='~/.shackles.yaml'
            , help='the library of potential actions that can be executed '
            '(default=~/.shackles.yaml)')
    args.add_argument('-c', '--command'
            , help="the command file to be executed (default=stdin)")
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
    if True:
        # Override the executor if noop option is specified
        executor = noop_exec

    return run_shell(library, executor, cmd_data, stdout)

if __name__ == "__main__":
    exit(main())
