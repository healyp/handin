#! /usr/bin/env bash

function print_usage() {
  echo "./pmonitor.sh COMMAND ARGS"
  exit 1
}

ARGS="$@"
CONFIG="syscalls.conf"
LOG="syscalls.log"
TMP="/tmp/strace.file"

if [ ! -f "$CONFIG" ]; then
  echo "syscalls.conf does not exist"
  exit 1
fi

mapfile -t SYS_CALLS < "$CONFIG"

echo -e "Log of syscalls that were in syscalls.conf made:\n" > "$LOG"

TRACE=""

for val in "${SYS_CALLS[@]}"; do
  if [[ ! "$val" == "#"* ]] && [ ! -z "$val" ]; then
    # this is not a comment and it is not an empty line
    TRACE="$TRACE,$val"
  fi
done

# strace will work as follows:
#   -o "$TMP" specifies to output to the file specified in "$TMP"
#   -f tells strace to follow all child processes/threads
#   -y attempts to print the full path specified in a syscall (does not always work)
#   -e trace="$TRACE" filters the syscalls by the syscalls found in syscalls.conf
#   -e signal=none tells strace to not output any signals to the file
#   -qqq is a way of telling strace to keep quiet about all suppressible messages such as process exited etc.
#   $ARGS is the command and arguments as passed into the script
strace -o "$TMP" -f -y -e trace="$TRACE" -e signal=none -qqq $ARGS

exit_code="$?"

if [ "$exit_code" -ne "0" ]; then
  exit "$exit_code"
fi

cat "$TMP" >> "$LOG"
rm -f "$TMP"

exit "$exit_code"