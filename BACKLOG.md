## Add a Call object
Some object that contains info about a remote call: the name, and any arguments

## Support shell actions also
Too strict to not allow shell commands.  Putting cmd & all args on
a single line is so much easier in configuration that it should be supported.
The reason to not support it is it then allows templating the command,
but you can work around that with sudo or whatever anyway.
