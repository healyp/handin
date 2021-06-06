#! /usr/bin/bash

# This file "installs" the servers required for handin. It basically sets up services for the handin_file_server and
# system_server. The file server will be known as handinfs and the system_server, just handin.
# It should be run from the root of the directory
# It installs a script start_handin which can start any py file specified that is present in the src directory
# E.g. start_handin handin_file_server.py (just name of file without path) would start the server
# If you add the installation directory to PATH, you can start a handin file from anywhere

function print_usage() {
  echo -e "./install -uninstall | [-u user] [--no-services | -start]\n\t-u user\n\t\tAn optional flag to specify the user to start the handin servers.
          \tThey must be in the docker group. If left blank, the output of the logname command is used\n\t--no-services\n\t\tSpecify this just to install the start_handin script
          \n\t-start\n\t\tOptional flag to start the services after installation. This doesn't make sense with --no-services, so it's either --no-services or -start, not both
          \n\t-uninstall\n\t\tUninstalls handin service files and removes the start_handin script\n\n
          This script must be run from the root of the project and as root user if --no-services is not provided.
          Uninstall doesn't require root if it was installed with --no-services"
}

function display_error() {
  print_usage
  exit 1
}

function create_service_file() {
  description="$1"
  user="$2"
  handin_home="$3"
  server="$4"
  service_name="$5"

  service=$(sed -e "s|{HANDINHOME}|$handin_home|g" -e "s|{DESCRIPTION}|$description|g" -e "s|{USER}|$user|g" \
          -e "s|{SERVER}|$server|g" handin.service.template)

  echo "Creating $service_name"
  echo "$service" > "/etc/systemd/system/$service_name"

  echo "Enabling $service_name"
  systemctl enable "$service_name"

  if [ "$?" -ne "0" ]; then
    echo "ERROR: Enabling $service_name failed, exiting..."
    exit 3
  fi
}

function create_start_script() {
  echo "Creating start_handin script"
  handin_home="$1"
  user="$2"

  start_handin=$(sed -e "s|{HANDINHOME}|$handin_home|g" start_handin.sh.template)
  echo "$start_handin" > "$PWD/start_handin"
  chown $user "$PWD/start_handin"
  chgrp $user "$PWD/start_handin"
  chmod +x "$PWD/start_handin"
}

function check_root() {
  if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script needs to be run as root"
    exit 2
  fi
}

function uninstall() {
  uninstalled="false"
  root_checked="false"

  if [ -f "/etc/systemd/system/handin.service" ]; then
    check_root
    root_checked="true"
    echo "Disabling handin.service"
    systemctl stop handin.service
    systemctl disable handin.service

    echo "Removing handin.service"
    rm /etc/systemd/system/handin.service
    uninstalled="true"
  fi

  if [ -f "/etc/systemd/system/handinfs.service" ]; then
    if [ "$root_checked" == "false" ]; then
      check_root
      root_checked="true"
    fi
    echo "Disabling handinfs.service"
    systemctl stop handinfs.service
    systemctl disable handinfs.service

    echo "Removing handinfs.service"
    rm /etc/systemd/system/handinfs.service
    uninstalled="true"
  fi

  if [ "root_checked" == "true" ]; then
    systemctl daemon-reload
  fi

  if [ -f "start_handin" ]; then
    echo "Removing start_handin script"
    rm start_handin
    uninstalled="true"
  fi

  if [ "$uninstalled" == "true" ]; then
    echo "handin uninstalled"
  else
    echo "Nothing to uninstall"
  fi
}

COUNT="$#"

user=$(logname)
services_flag=""

while [ "$COUNT" -gt "0" ]; do
  case "$1" in
    -u) if [[ $2 != -* ]]; then
          user="$2"
          shift 2
          COUNT=$(expr $COUNT - 2)
        else
          user=""
          shift
          COUNT=$(expr $COUNT - 1)
        fi
        ;;
    -uninstall) uninstall
                exit 0
                ;;
    -start) if [ ! -z "$services_flag" ]; then
              display_error
            else
              services_flag="$1"
              shift
              COUNT=$(expr $COUNT - 1)
            fi
            ;;
    --no-services) if [ ! -z "$services_flag" ]; then
                     display_error
                  else
                    services_flag="$1"
                    shift
                    COUNT=$(expr $COUNT - 1)
                  fi
                  ;;
    *) display_error
        ;;
    -h) print_usage
        exit 0
        ;;
  esac
done

no_services="false"
start="false"

if [ -z "$user" ]; then
  display_error
else
  user_exists=$(grep "$user" /etc/passwd)

  if [ -z "$user_exists" ]; then
    echo "ERROR: User $user does not exist"
    exit 4
  fi

  in_group=$(id -nG "$user" | grep -w "docker")

  if [ -z "$in_group" ]; then
    echo "ERROR: User $user is not in the docker group"
    exit 4
  fi
fi

if [ ! -z "$services_flag" ]; then
  if [ "$services_flag" == "-start" ]; then
    start="true"
  elif [ "$services_flag" == "--no-services" ]; then
    no_services="true"
  else
    display_error
  fi
fi

if [ "$no_services" != "true" ]; then
  check_root
fi

echo "Installation directory is $PWD"

if [ "$no_services" == "false" ]; then
  echo "Using user $user to set up the services for handin (system_server) and handinfs (handin_file_server)"
fi

create_start_script "$PWD" "$user"

if [ "$no_services" == "false" ]; then
  create_service_file "Handin System Server" "$user" "$PWD" "system_server.py" "handin.service"
  create_service_file "Handin File Server" "$user" "$PWD" "handin_file_server.py" "handinfs.service"

  systemctl daemon-reload

  if [ "$start" == "true" ]; then
    echo "Starting handin.service"
    systemctl start handin.service
    systemctl status handin.service

    echo "Starting handinfs.service"
    systemctl start handinfs.service
    systemctl status handinfs.service
  fi
fi

echo "Handin successfully installed"
