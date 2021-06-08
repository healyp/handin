#include <sys/ptrace.h>
#include <sys/reg.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <unistd.h>
#include <asm/unistd_64.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>

/**
	* This program allows a command to be run and monitor for certain system calls and
	* log them if they are encountered by the command. These system call numbers can be defined in
	* the syscalls.conf file.
	*
	* The default syscall numbers are those that are related to the unlink
	* and rename syscalls which are called by remove operations and move operations
	* respectively.
	*
	* The syscall numbers can be found in /usr/include/x86_64-linux-gnu/unistd_64.h
	*/

/**
	* 50 should be plenty syscalls to monitor but if more needs to be provided, pass
	* -DSYS_CALLS_BUFFER=<val> into the compiler
	*/
#ifndef SYS_CALLS_BUFFER
#define SYS_CALLS_BUFFER 50
#endif

/**
	* Our array containing the syscall numbers that are being monitored
	*/
int SYS_CALLS[SYS_CALLS_BUFFER];
/**
	* The number of syscall numbers that have been loaded
	*/
int LOADED_SYS_CALLS = 0;
/**
	* An array of syscalls that are logged. It is to be set up as follows:
	* 1. Find the smallest syscall number in SYS_CALLS
	* 2. Set the size of the array to be the syscall number + 1
	* Set up this way means we can do:
	* if (!LOGGED_SYS_CALLS[syscall]) {
	*		// log here
	*		LOGGED_SYS_CALLS[syscall]
	*	}
	*/
int *LOGGED_SYS_CALLS = NULL;
/**
	* The max index we can use to access the LOGGED_SYS_CALLS array
	*/
int MAX_LOGGED_INDEX = 0;
/**
	* This will be 1 if the loaded syscalls were found in the config file. If the defaults
	* were loaded, it will be 0
	*/
int DEFINED_IN_FILE = 0;

/**
	* Loads the syscalls from the config file
	*/
void load_file_configs(FILE *file) {
	int i = 0;
	DEFINED_IN_FILE = 1;
	size_t len = 255;
	ssize_t read;

	char *line = NULL;
	while ((read = getline(&line, &len, file)) != -1) {
		int syscall = atoi(line);

		if (syscall != 0) {
			if (i < SYS_CALLS_BUFFER) {
				SYS_CALLS[i++] = syscall;
			} else {
				fprintf(stderr, "SYS_CALLS_BUFFER exceeded, compile with -DSYS_CALLS_BUFFER=<val> with val large enough to hold all the sys call numbers");
				exit(1);
			}
		}
	}
	free(line);

	fclose(file);
	LOADED_SYS_CALLS = i;
}

/**
	* Loads default syscalls in the event that syscalls.conf cannot be found
	*/
void load_default_configs() {
    DEFINED_IN_FILE = 0;
    SYS_CALLS[0] = __NR_unlink;
    SYS_CALLS[1] = __NR_mq_unlink;
    SYS_CALLS[2] = __NR_unlinkat;
    SYS_CALLS[3] = __NR_rename;
    SYS_CALLS[4] = __NR_renameat;
    SYS_CALLS[5] = __NR_renameat2;
    LOADED_SYS_CALLS = 6;
}

/**
	* Generate the LOGGED_SYS_CALLS array. The array is defined so that
	* LOGGED_SYS_CALLS[syscall] can be read to be either 0 or 1
	*/
void generate_logged_syscalls_array() {
	int largest_index = 0;
	for (int i = 1; i < LOADED_SYS_CALLS; i++) {
		if (SYS_CALLS[i] > SYS_CALLS[largest_index]) {
			largest_index = i;
		}
	}

	int max_index = SYS_CALLS[largest_index] + 1;
	LOGGED_SYS_CALLS = (int*)calloc(max_index, sizeof(int));
	MAX_LOGGED_INDEX = max_index - 1;

	if (LOGGED_SYS_CALLS == NULL) {
		fprintf(stderr, "Memory Allocation error\n");
		exit(1);
	}
}

/**
	* Configure the tracer either from the config file or defaults if not found
	*/
void load_configs() {
	FILE *file = fopen("syscalls.conf", "r");

	if (file != NULL) {
		load_file_configs(file);
	} else {
		load_default_configs();
	}

	generate_logged_syscalls_array();
}

int do_child(int argc, char **argv);
int do_trace(pid_t child);

/**
	* Starts our syscall tracing process
	*/
int main(int argc, char **argv) {
  if (argc < 2) {
  	fprintf(stderr, "Usage: %s prog args\n", argv[0]);
    exit(1);
  }

	pid_t child = fork();
  if (child == 0) {
  	return do_child(argc-1, argv+1);
  } else {
    load_configs(); // only the tracer needs the configs, so load them here
    return do_trace(child);
  }
}

/**
	* Executes our process with the PTRACE_TRACEME flag
	*/
int do_child(int argc, char **argv) {
	ptrace(PTRACE_TRACEME, 0, NULL, NULL);
    char *args [argc+1];
    memcpy(args, argv, argc * sizeof(char*));
    args[argc] = NULL;
    return execvp(args[0], args);
}

/**
	* Checks if the provided syscall is allowed or not
	*/
int sys_call_allowed(int syscall) {
	for (int i = 0; i < LOADED_SYS_CALLS; i++) {
		if (syscall == SYS_CALLS[i])
			return 0;
	}

	return 1;
}

/**
	* Logs the syscall made to the provided file if it has not been already logged
	*/
void log_syscall(FILE *file, int syscall) {
	if (syscall > MAX_LOGGED_INDEX) // this syscall is not within our syscall array if it is greater than the max index, so don't log
		return;

	if (!LOGGED_SYS_CALLS[syscall]) {
		fprintf(file, "Dangerous syscall(s) (%d) made by program\n", syscall);
		LOGGED_SYS_CALLS[syscall] = 1;
	}
}

/**
	*	Performs the trace of the child provided
	*/
int do_trace(pid_t child) {
    int status, syscall, retval;
	FILE *log_file = fopen("syscalls.log", "w");
	if (DEFINED_IN_FILE) {
		fprintf(log_file, "Log of syscalls made (defined in syscalls.conf). System calls are only logged once each but may have occurred multiple times:\n\n");
	} else {
		// the syscalls.conf file could not be found, so we fall back to the syscalls defined in load_default_configs()
		fprintf(log_file, "Log of syscalls made (defaults). System calls are only logged once each but may have occurred multiple times:\n\n");
	}

    while(1) {
        waitpid(child, &status, 0);
        if (WIFEXITED(status) || WIFSIGNALED(status)) break;

        syscall = ptrace(PTRACE_PEEKUSER, child, sizeof(long)*ORIG_RAX, NULL);
        if (!sys_call_allowed(syscall)) {
			// syscall is not allowed, so log it to the log_file
            log_syscall(log_file, syscall);
        }
		ptrace(PTRACE_SYSCALL, child, 0, 0);
    }

	fclose(log_file);
	free(LOGGED_SYS_CALLS);

	return 0;
}
