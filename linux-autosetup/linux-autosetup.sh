#!/bin/bash
# *** https://stackoverflow.com/questions/8455991/elegant-way-for-verbose-mode-in-scripts
version="v2.0.0-rc2"

#########################
# VARIABLE DECLARATIONS #
#########################

# Overwrite $HOME with sudo user
declare HOME="$(eval echo ~${SUDO_USER})"

declare MODE=""
declare -a ENTRIES=()

# Stores all app names
declare -a apps
# Stores all apps with backups
declare -a appBackups
# Stores app groups as keys
# Stores apps separated by spaces as data
declare -A appGroups
# String used to substitute app names
declare app='$app'

# Stores all archives
declare -a archives
# Stores all archives
declare -A archiveGroups

##########################
# CONFIGURABLE VARIABLES #
##########################

# If a command call uses cd, this will allow remaining in proper dir
declare SCRIPT_WORKING_DIR="$(pwd)"
# Default configuration folder
declare CONFIG_FOLDER="./config"
# Where modules are stored; e.g classes, event functions
declare MODULES_DIR="./.modules"
# Where backups will be created first - avoids possibility of bad dumps if backup commands fail somehow
declare TMP_DIR="/tmp/linux-autosetup"
# Determines whether errors should prompt users to fix: "1" = true, "0" = false
declare SKIP_ERRORS="0"

# Where application backups go
declare APP_BACKUP_DIR="./app-backups"
# Whether app backups should also be installed
# "" = ask user what to set to, "-1" = no, "0" = prompt user, "1" = yes
declare APP_INSTALL_BACKUPS=""
# Default app backup type - "COPY", "HARDLINK"
declare DEFAULT_APP_BACKUP_TYPE="COPY"
# Default install command used if one is not specified for app
# $app is substituted for app name
declare DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $app will not be installed until this is done."

# Where archives go
declare ARCHIVE_BACKUP_DIR="./archives"
# Default archive type - "COPY, COMPRESS, ENCRYPT"
declare DEFAULT_ARCHIVE_BACKUP_TYPE="COPY"

# Where to dump files
declare DUMP_DIR="./dump"

################
# SCRIPT SETUP #
################

# Print information about the script, like copyright or help
printScriptInfo() {
	echo "Linux-autosetup, version $version"
	if [ "$1" = legal ]; then
		echo "Copyright (C) 2021 Aurtzy"
			if [ "$2" = 'help' ]; then
				echo "Linux-autosetup comes with ABSOLUTELY NO WARRANTY; for details run this script with the '--warranty' option. This is free software, and you are welcome to redistribute it under certain conditions; run this script with the '--copyright' option for details."
			elif [ "$2" = 'warranty' ]; then
				echo "This program is distributed in the hope that it will be useful, WITHOUT ANY WARRANTY; without even the implied warranty of or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details."
			elif [ "$2" = 'copyright' ]; then
				echo "This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version."
			fi
	elif [ "$1" = 'help' ]; then
		echo "Usage:"
		echo "    bash $0 [options]"
		echo "    bash $0 [mode options] [mode]"
		echo "    bash $0 [mode options] [mode=i/b] entries ..."
		echo "modes:"
		echo "    -i  --install       	Run this script in install mode."
		echo "    -b  --backup        	Run this script in backup mode."
		echo "        --debug         	Run this script in debug mode."
		echo "                        	Not intended for normal use."
		echo
		echo "mode options:"
		echo "    -c  --config <file> 	Use specified config file."
		echo "                        	If no / is present, script assumes default config dir."
		echo
		echo "options:"
		echo "    -h  --help          	Print this help."
		echo "    -v --version        	Print current version."
		echo

	fi
}

# If options are empty, enter basic mode chooser
if [ "$1" = "" ]; then
	echo "This mode chooser is limited to only choosing modes."
	echo "If you want to see additional options for running this script"
	echo "in the future, run this script with '--help'."
	while true; do
		read -p "[i/b/?]: " userIn
		case "$userIn" in
			i*) bash "$0" "--install"; exit $?;;
			b*) bash "$0" "--backup"; exit $?;;
			"?") echo "Run this script in install/backup mode.";;
		esac
	done
fi

# Parse options
for ((i=1; i <= ${#@}; i++)); do
	case "${!i}" in
		"-i" | "--install")
			MODE=INSTALL
			ENTRIES=("${@:$(expr $i + 1)}")
			break;;
		"-b" | "--backup")
			MODE=BACKUP
			ENTRIES=("${@:$(expr $i + 1)}")
			break;;
		"--debug")
			MODE=DEBUG;;
		"-c" | "--config")
			i=$(expr $i + 1)
			declare -g CONFIG_FILE="${!i}";;
		"-h" | "--help")
			printScriptInfo help usage
			exit;;
		"-v" | "--version")
			printScriptInfo
			exit;;
		"--warranty")
			printScriptInfo legal warranty
			exit;;
		"--copyright")
			printScriptInfo legal copyright
			exit;;
		*)
			echo "Error: Argument ${!i} not recognized"
			exit 1;;
	esac
done

if ! [ "$MODE" ]; then
	echo "Error: mode was not set."
	exit 1
fi

# Force run as root
if [ $(id -u) -ne 0 ]; then
	echo
	echo "This script must be run with root priviliges."
	sudo bash "$0" "$@"
	exit $?
else
	printScriptInfo legal help
fi

#############
# FUNCTIONS #
#############

# initialize modules
init_modules() {
	. "$MODULES_DIR/class_headers.sh"
	. "$MODULES_DIR/event_functions.sh"
	. "$MODULES_DIR/autosetup_functions.sh"

	. "$MODULES_DIR/init_config.sh"
}

mkdir() {
	sudo -u "$SUDO_USER" mkdir -p "$1" || mkdir -p "$1"
}

# Dumps file/folder into $DUMP_DIR
# Dump must be initialized before using in a function.
# $1 = path to file(s) $2 = dump name to be dumped
# Special case: if $1 = "INITIALIZE,"
# create new dump folder iteration with $2 as $dumpName
dumpTo() {
	declare dumpPath="$DUMP_DIR/$1"
	declare -a paths=("${@:2}")

	echo "dump(): Initializing $dumpName dump directory"
	declare -i i=1
	while [ -d "$dumpPath/$i" ]
	do
		echo "dump(): $dumpPath/$i already exists."
		i+=1
		echo "dump(): Trying $dumpPath/$i..."
	done
	mkdir "$dumpPath/$i" && echo "dump(): Dump initialized at $dumpPath/$i"

	for path in "${paths[@]}"; do
		if [ -e "$path" ]; then
			mv "$path" "$dumpPath/$i"
		else
			echo "dump(): Error: $path was not found"
		fi
	done
}

########
# INIT #
########

init_modules

########
# MODE #
########

# Debug mode; user is put into input-reader which acts like a normal shell
# In addition to normal Bash commands, user can call individual functions
# set by the script
debug() {
	echo
	echo "Entering debug mode."
	while
	appInstallBackups=0
	read -p ": " userIn
	do
		eval $userIn
	done
}

case "$MODE" in
	DEBUG) debug;;
	INSTALL) autosetup-install;;
	BACKUP) autosetup-backup;;
esac
exit 0
