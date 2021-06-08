"""
    This module provides a means to execute student's code in a sandboxed docker container
    It provides a means of wrapping a compilation command and a run command into a single
    execute call. Where compilation does not make sense, for example, Python, compilation
    is ignored.

    Provided that compilation doesn't fail (if it does the returned ExecutedProcess has a tag 'compilation'
    with the stderr output), an ExecutedProcess with tag 'run' is returned.

    Supported languages have to be backed by a docker image that is able to run those commands.
    Currently, the supported languages are gcc (c and c++), python, java and lua.
    build-docker-images.sh has to be run once for this module to work.

    The language (if not specified) is extracted from the filename extension, e.g. main.c, the
    language will be c.

    An example call is:
    exec1 = execute("main.c", run_command="./main", compilation_command="gcc main.c -o main")

    This specifies how to compile the program and then how to run it. main.c is expected to be in
    the current directory here, or else pass in the path.
    exec1 is a ExecutedProcess object. See the class below for the fields it contains

    An example of how to use this is as follows:
        import handinexecutor

        with handinexecutor.start() as executor:
            compile_proc = executor.compile(....)
            # do something with compile_proc
            run_proc = executor.run(....)
            # do something with run_proc
"""

import epicbox
import os
import subprocess
from contextlib import contextmanager

import const

_all_ = ['ExecutedProcess', 'HandinExecutorException', 'start']

# The supported profiles which run the associated docker images. If a new language is added, a new docker image must be created for that language,
# and associated profiles and execute calls
PROFILES = {
    'gcc_compile': {
        'docker_image': 'handin-gcc',
        'user': 'root',
    },
    'gcc_run': {
        'docker_image': 'handin-gcc',
        'user': 'handin',
        'network_disabled': True,
    },
    'java_compile': {
        'docker_image': 'handin-java',
        'user': 'root',
    },
    'java_run': {
        'docker_image': 'handin-java',
        'user': 'handin',
        'network_disabled': True,
    },
    'python_run': {
        'docker_image': 'handin-python',
        'user': 'handin',
        'network_disabled': True,
    },
    'lua_run': {
        'docker_image': 'handin-lua',
        'user': 'handin',
        'network_disabled': True,
    }
}

"""
    The languages supported by handin_executor at the moment.
    These have a mapping to docker images in the docker/ directory. Example, python has handin-python image,
    java has handin-java image, c and c++ has handin-gcc image. A language cannot be supported without a docker image
"""
SUPPORTED_LANGUAGES = ["python", "java", "c", "c++", "lua"]

"""
    The mapping of file extensions to languages
"""
FILE_EXTENSION_MAPPINGS = {
    "py": "python",
    "pyo": "python",
    "pyc": "python",
    "java": "java",
    "c": "c",
    "cc": "c++",
    "cpp": "c++",
    "lua": "lua"
}

LANGUAGE_PROFILES = {
    "gcc": ["gcc_compile", "gcc_run"],
    "python": ["python_run"],
    "java": ["java_compile", "java_run"],
    "lua": ["lua_run"]
}

LANGUAGE_IMAGE_MAPPINGS = {
    "c": "handin-gcc",
    "c++": "handin-gcc",
    "python": "handin-python",
    "java": "handin-java",
    "lua": "handin-lua"
}

def _configure_executor():
    # The following is a "HACK" so we can use the defaults without specifying limits
    # each time. epicbox also uses /sandbox for its DOCKER_WORKDIR which does not have
    # the correct permissions for user handin

    execution_timeout = int(const.PROGRAM_EXECUTION_TIMEOUT)
    memory_limit = int(const.PROGRAM_MEMORY_LIMIT)
    epicbox.config.DEFAULT_LIMITS = {
        'cputime': execution_timeout,
        'realtime': execution_timeout,
        'memory': memory_limit,
        'processes': -1
    }
    epicbox.config.DOCKER_WORKDIR = "/home/handin"
    epicbox.configure(profiles=PROFILES)

class ExecutedProcess:
    """
        This class represents a process that has been executed. It wraps the tag the process represented.
        The tag may either be compilation or run. Compilation is a process that was run from the compilation_command
        but failed. Run is a process running the actual code and could either have been successful or failed
    """
    def __init__(self, tag: str="run", stdout: str="", stderr: str="", exit_code: int=0, timeout: bool=False):
        if tag != "run" and tag != "compilation":
            raise HandinExecutorException(f"Invalid tag passed to ExecutedProcess: {tag}")
        self.tag = tag
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.timeout = timeout

class HandinExecutorException(Exception):
    """
        This represents an exception of any error that occurred in this module
    """
    pass

def _check_images():
    """
        Checks if there are docker images for each of the languages
    """
    command = ["docker", "images"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    if stderr != "":
        raise HandinExecutorException("An error occurred checking docker status: " + stderr)

    for language in SUPPORTED_LANGUAGES:
        if language not in LANGUAGE_IMAGE_MAPPINGS:
            raise HandinExecutorException(f"There is no entry for {language} in LANGUAGE_IMAGE_MAPPINGS")
        image = LANGUAGE_IMAGE_MAPPINGS[language]

        if image not in stdout:
            raise HandinExecutorException("No docker image exists for language: " + language)

class _Executor:
    """
        This class represents an abstract executor machine that can execute commands.
        Not intended to be instantiated outside the start() method

        To create an instance of this class, do the following:
            with handinexecutor.start() as workdir:
                executor = handinexecutor.Executor(workdir)

                executor.compile(...) or executor.execute() calls here

        Attributes:
            last_executed   The last produced ExecutedProcess. None if no call to compile or execute has been made
    """
    def __init__(self, workdir):
        self._validate_workdir(workdir)
        self._workdir = workdir
        if const.PROGRAM_SYSCALL_MONITORING:
            self._setup_syscall_monitor()
        self.last_executed = None

    @staticmethod
    def _deduce_language(path_to_file, language=None):
        """
            Uses the path of the file to deduce the language if the provided language is None.
            The language parameter, if provided, would be provided from the compile_proc or execute methods.
            If language is provided, language is verified and returned
        """
        if path_to_file is not None:
            filename, file_extension = os.path.splitext(path_to_file)
        else:
            file_extension = ""

        if file_extension == "" and language is None:
            raise HandinExecutorException(
                "Cannot determine language as file does not have an extension and language is None")
        elif file_extension != "" and language is None:
            language = file_extension[1:]
            if language not in FILE_EXTENSION_MAPPINGS:
                raise HandinExecutorException("Cannot determine language from file extension")
            else:
                language = FILE_EXTENSION_MAPPINGS[language]

        if language not in SUPPORTED_LANGUAGES:
            raise HandinExecutorException(f"The language {language} is not supported")

        if language == "c" or language == "gcc":
            return "gcc"
        else:
            return language

    @staticmethod
    def _validate_workdir(workdir):
        """
            Validates that the workdir is one produced from start()
        """
        if workdir is None or not isinstance(workdir, epicbox.sandboxes._WorkingDirectory):
            raise HandinExecutorException(
                "workdir is not a valid workdir. Use with handin_executor.start() as workdir:")

    @staticmethod
    def _validate_files_list(files):
        if files is not None:
            length = len(files) != 0

            if length == 0:
                raise HandinExecutorException("An empty list of files was provided. Use None instead")

            for val in files:
                if not isinstance(val, dict):
                    raise HandinExecutorException("The list of files provided contains a value that is not a dictionary")
                else:
                    keys = val.keys()
                    if len(keys) != 2:
                        raise HandinExecutorException("The dictionary for defining a file needs to have only 2 keys")
                    else:
                        if "name" not in keys and "content" not in keys:
                            raise HandinExecutorException("The dictionary for defining a file needs to have name and content")

    def _setup_syscall_monitor(self):
        """
            Sets up the syscall_monitor.c file for the executor
        """
        with open(const.SRCDIR + "/cutils/syscalls.conf", 'rb') as file:
            config = file.read()
        files = [{"name": "syscalls.conf", 'content': config}]
        proc = self.compile(path_to_file=const.SRCDIR + "/cutils/syscall_monitor.c",
                                compile_command="gcc syscall_monitor.c -o syscall_monitor", language="c", files=files)
        if proc.exit_code != 0:
            raise HandinExecutorException("Failed to setup syscall_monitor with stderr: " + proc.stderr)

    @staticmethod
    def _compile(file, compile_command, compilation_profile, workdir, other_files) -> ExecutedProcess:
        """
            Compiles the file with the provided command, profile and working directory
        """
        with open(file, 'rb') as f:
            code = f.read()

        file = os.path.basename(file)

        files = [{'name': file, 'content': code}]
        _Executor._validate_files_list(other_files)

        if other_files is not None:
            files.extend(other_files)

        result = epicbox.run(compilation_profile, compile_command,
                             files=files,
                             workdir=workdir)
        return ExecutedProcess(tag="compilation", stdout=result["stdout"].decode(),
                               stderr=result["stderr"].decode(), exit_code=result["exit_code"],
                               timeout=result["timeout"])

    @staticmethod
    def _run(file, run_command, run_profile, stdin, workdir, other_files) -> ExecutedProcess:
        """
            Executes the file by compiling it if compilation_command is not none. If compilation fails,
            an ExecutedProcess with the tag "compilation" is returned with the stderr streams. The code is then run using
            the run_command returning ExecutedProcess with run tag and stdout and stderr stream outputs

            The run profile is the profile of the docker images outlined above
        """
        if file is not None:
            with open(file, 'rb') as f:
                code = f.read()
        else:
            file = "not-exists"
            code = b""

        file = os.path.basename(file)

        try:
            if ("python" in run_command or "lua" in run_command) and len(run_command.split()) < 2:
                run_command = run_command + " " + file
            files = [{'name': file, 'content': code}]  # skip compilation and run file directly

            if other_files is not None:
                _Executor._validate_files_list(other_files)
                files.extend(other_files)

            if run_command is None:
                raise HandinExecutorException("No run_command provided for execution")
            else:
                result = epicbox.run(run_profile, run_command, files=files, workdir=workdir, stdin=stdin)
                return ExecutedProcess(tag="run", stdout=result["stdout"].decode(),
                                       stderr=result["stderr"].decode(), exit_code=result["exit_code"],
                                       timeout=result["timeout"])
        except Exception as e:
            if isinstance(e, HandinExecutorException):
                raise e
            raise HandinExecutorException("An exception occurred executing the file") from e

    def compile(self, path_to_file: str, compile_command: str, language: str = None, files: list = None) -> ExecutedProcess:
        """
            Compiles the provided file. If the language does not have a compile profile, it is not a compiled language
            and will be run as an executed process but returned with a compilation tag

            You can provide an extra list of files that the compilation might require with the files parameter, with each value
            taking the form {'name': <name>, 'content': contents}
        """
        language = self._deduce_language(path_to_file, language)

        keys = [key for key in PROFILES.keys() if "compile" in key]

        if language + "_compile" not in keys:
            print("Compilation not expected for language " + language + ". Executing instead with tag compilation")
            proc = self.run(path_to_file=path_to_file, run_command=compile_command, language=language, stdin=None, files=files)
            proc.tag = "compilation"
            self.last_executed = proc
            return proc
        else:
            proc = self._compile(file=path_to_file, compile_command=compile_command,
                            compilation_profile=LANGUAGE_PROFILES[language][0], workdir=self._workdir, other_files=files)
            self.last_executed = proc
            return proc

    def run(self, path_to_file: str, run_command: str, language: str = None, stdin: str = None, files: list = None) -> ExecutedProcess:
        """
            It takes the path to the file to run on the container and execute on the docker container, the command to run the program,
            an optional language parameter (if not provided, the language is deduced from the file extension). If language cannot
            be determined or is not supported, an exception is thrown.

            You can provide an extra list of files that the execution might require with the files parameter, with each value
            taking the form {'name': <name>, 'content': contents}

            run_command is wrapped by a call to syscall_monitor to monitor for dangerous syscalls. The log for it can be retrieved
            using copy_syscall_log
        """
        language = self._deduce_language(path_to_file, language)

        run_profiles = LANGUAGE_PROFILES[language]
        if len(run_profiles) == 1:
            run_profile = run_profiles[0]
        else:
            run_profile = run_profiles[1]

        if const.PROGRAM_SYSCALL_MONITORING:
            run_command = "./syscall_monitor " + run_command

        print(run_command)

        proc = self._run(file=path_to_file, run_command=run_command, run_profile=run_profile, stdin=stdin,
                         workdir=self._workdir, other_files=files)
        self.last_executed = proc
        return proc

    def copy_syscall_log(self, destination_path: str, test_tag):
        """
        Retrieve the syscall monitor log for the syscalls that are considered dangerous that were made, if any, from a previous
        call to run
        :param destination_path: the destination path to copy the file to
        :param test_tag: the tag to prepend onto syscalls.log as test_tag-syscalls.log
        :return: true if successful, false if not
        """
        if const.PROGRAM_SYSCALL_MONITORING:
            proc = _Executor._run(file=None, run_command="cat syscalls.log", run_profile="gcc_run", stdin=None, workdir=self._workdir, other_files=None)
            if proc.exit_code == 0 and proc.stderr == "":
                if os.path.isdir(destination_path):
                    path = f"{destination_path}/{test_tag}-syscalls.log"
                    with open(path, 'w+') as file:
                        file.write(proc.stdout)

                    return True

            return False
        else:
            raise HandinExecutorException("PROGRAM_SYSCALL_MONITORING is disabled in conf.yaml")

@contextmanager
def start():
    """
        Call this in a with statement to retrieve the executor object
    """
    with epicbox.working_directory() as workdir:
        yield _Executor(workdir)

_check_images()
_configure_executor()