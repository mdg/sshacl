## Clarify Terminology
Command is heavily overloaded and should be untangled.  Maybe switch Command
class to be Action or something.

## Add a Call object
Some object that contains info about a remote call: the name, and any arguments

## Missing files should be reported w/o a stack trace
Stack trace isnt necessary to report a missing file, just a
regular error message would be better
