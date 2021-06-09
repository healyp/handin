# Extending handin_file_server
Using the file_server_commands directory, you can extend the requests that the
server can handle. The rules and steps on how to extend it are as follows.

It makes the handin_file_server extensible so that if it needs to handle a new
request, you just create a new py file in this directory following the below rules, a new constant identifying the command name that the clients should send
in a Request (this constant also is used as a lookup key in the file server to
find the appropriate module to handle that request).

Theoretically, this could be extended even more to generalise the server to handle any request at all from a client and doesn't have to be strictly a server for interacting with ".handin" files. But for the sake of distributed design, we have a different server for the system

## Rules
- The files must be created in src/file_server_commands.
- There must be one file with only one class in it for each command
- Any files the class may need to process the request should be stored outside of the file_server_commands directory and imported
- The file can be named whatever you like, but a guideline is to have it similar
to the name of the command given in the const.py file (more on this soon). For example, if the command is FileServerCommands.AUTHENTICATE_LECTURER, remove the
underscore and convert to camelcase, so you have AuthenticateLecturer.py
- The file must contain a single class with the same name as the filename without .py at the end.
- The file must inherit AbstractCommand and implement handleRequest which takes
a handin_messaging.Request object

## Steps
1. In file_server_commands, create the file with the naming convention set out
above
2. Inside the file at the top, add the following lines (as a minimum, you may
  require other imports) with new lines after each import:
  `from const import FileServerCommands
  from file_server_commands.AbstractCommand import AbstractCommand
  from handin_messaging import *`
  If you need to use helper functions (such as authenticate_lecturer) from handin_file_server.py and the request_xx logging methods, type:
  `from handin_file_server import *`
  If you need more variables from const (or all), add them to the const import or replace with *
3. Create a class with the same name as the file and without the .py extension and have it extend AbstractCommand
4. Specify a COMMAND attribute with it equalling the const.FileServerCommands value. If it is a new command, you will need to define it in const.FileServerCommands and add the const to the VALID_COMMANDS list. e.g.:
  `COMMAND = FileServerCommands.AUTHENTICATE_LECTURER`
5. Create the constructor which just calls `super().__init__()` with no parameters
6. Create the handleRequest method which will handle and respond to the request
7. Now with the constant defined in const.FileServerCommands, and the COMMAND attribute (be careful not to miss these as the server will ignore the file if not extending AbstractCommand or python will throw an error if COMMAND is not defined), when the server is launched, it will automatically (handin_file_server.log in debug mode should have the class included in the list of commands loaded) load in all the defined commands and when the server receives a request with a Command matching a loaded file, it will call its handleRequest method and pass in the received Request.

## File Template
This is a template of a file implementing the command. Note, FileName.py where FileName is the name of the file and subsequently class and COMMAND_NAME is the name of the constant identifying the command in const.py
![img](../../images/extending_file_server.png)

## Caveat
Some IDE's (example PyCharm) may show errors in the Python file for missing imports. You can ignore
these as they will be resolved when the file server imports the file
