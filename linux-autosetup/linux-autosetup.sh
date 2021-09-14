#!/bin/bash

# Require run as root
#if [ $(id -u) -ne 0 ]; then
#	echo "Please run script as root! Exiting..."
#	exit 1
#fi

# Stores all app names
declare -ag apps

# Stores app groups as keys
# Stores apps separated by spaces as data
declare -Ag appGroups

# "Booleans": -1=false/no, 0=unset, 1=true/yes
# Whether app backups should also be installed - 0 = always ask
# Should reset to 0 after every user command or AppGroup install
declare -i appInstallBackups=0

# String used to substitute app names
declare name='$name'

##########################
# CONFIGURABLE VARIABLES #
##########################

# If a command call uses cd, this will allow remaining in proper dir
declare SCRIPT_WORKING_DIR="$(pwd)"
# Default configiguration files
declare -a CONFIG_FILES=("")
# Where classes are stored
declare CLASSES_DIR="./classes"

# Where application backups go
declare APP_BACKUP_DIR="./app-backups"
# Default app backup type - "COPY", "HARDLINK"
declare APP_BACKUP_TYPE="COPY"
# Default install command used if one is not specified for app
# $nameSubstitution is substituted for app name
declare DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $name will not be installed until this is done."

# Where to dump files
declare DUMP_DIR="./dump"

####################
# GLOBAL FUNCTIONS #
####################

# Dumps file/folder into $DUMP_DIR
# Dump must be initialized before using in a function.
# $1 = path to file(s) $2 = dump name to be dumped
# Special case: if $1 = "INITIALIZE," 
# create new dump folder iteration with $2 as $dumpName
dump() {
	declare path="$1"
	declare dumpName="$2"
	if [ "$1" = 'INITIALIZE' ]; then
		echo "dump(): Initializing $dumpName dump directory"
		declare -i i=1
		while [[ -d "$DUMP_DIR/$dumpName/$i" ]]
		do
			echo "dump(): $DUMP_DIR/$dumpName/$i already exists."
			i+=1
			echo "dump(): Trying $DUMP_DIR/$dumpName/$i..."
		done
		echo "dump(): Dump initialized at $DUMP_DIR/$dumpName/$i"
		mkdir -p "$DUMP_DIR/$dumpName/$i"
	elif [[ -d "$path" || -f "$path" ]]; then
		declare -i i=1
		while [ -d "$DUMP_DIR/$dumpName/$i" ]
		do
			i+=1
			continue
		done
		i=i-1
		mv "$path" "$DUMP_DIR/$dumpName/$i"
	else
		echo "dump(): Error: $path was not found"
	fi
}

# String converter methods to allow functionality with Bash
# Convert '-' and $hyphenConversion from and to each other
convertHyphens() {
	echo ${1//-/_}
}

# App constructor caller
# $1=name, $2=installCommand, $3=backupType, ${@:4}=sourcePaths
App() {
	if [ "$1" = '' ]; then
		echo "Error: app name parameter was empty."
		return
	fi
	fields="app_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/App/$1/g" "$CLASSES_DIR"/App.class))
	$1.constructor "$2" "$3" "${@:4}"
}
# App group constructor caller
# $1=name
AppGroup() {
	if [ "$1" = '' ]; then
		echo "Error: AppGroup name parameter was empty."
		return
	fi
	fields="appGroup_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/AppGroup/$1/g" "$CLASSES_DIR"/AppGroup.class))
	$1.constructor ${@:2}
}

# Initialize app groups in appGroups array
initializeAppGroups() {
	for appGroup in $(appGroups); do
		AppGroup $appGroup "${appGroups[$appGroup]}"
	done
}

# Return all apps separated by spaces
apps() {
	echo "${apps[*]}"
}

# Return all appGroups separated by spaces
appGroups() {
	echo "${!appGroups[*]}"
}

# Prompt user to input yes/no
# In special cases, using -y/-n autofills y/n for all prompts
# Returns: -n=-1, n=0, y=1, -y=2
promptYesNo() {
    while true; do
        read -p "$* [y/n]: " userIn
        case $userIn in
            [Yy]*) echo 1; return;;  
            [Nn]*) echo 0; return;;
            -[Yy]*) echo 2; return;;
            -[Nn]*) echo -1; return;;
        esac
    done
}

runAtEnd() {
	return
}

###############
# SCRIPT BODY #
###############

# Import config autosetup.conf
. config/linux-autosetup.conf.sh

# Choose CONFIG_FILE - if there's only one in the array, then automatically choose
if [ ${#CONFIG_FILES[@]} -gt 1 ]; then
	while true; do
		echo "Which config file do you want to use?"
		for i in ${!CONFIG_FILES[*]}; do
			echo "$i ${CONFIG_FILES[$i]}"
		done
		read -p "Enter the index of the config file: " userIn
		if [[ -z "$userIn" || "$userIn" > 'a' ]]; then
			continue
		fi
		declare -i i="$userIn"
		if [[ $i -ge 0 && $i -lt ${#CONFIG_FILES[@]} ]]; then
			declare CONFIG_FILE="${CONFIG_FILES[$i]}"
			break
		fi
	done
else
	CONFIG_FILE="${CONFIG_FILES[0]}"
fi

# Import CONFIG_FILE & initialize stuff
echo "Initializing objects..."
. config/$CONFIG_FILE
initializeAppGroups
AppGroup allApps "${apps[*]}" # App group allApps; contains all apps
echo "All objects successfully initialized."

# Before starting script, ask user if the variables
# that have been set are okay with them. Then, proceed.
echo
echo "**Please double-check the variables that have been set."
echo "**Directories will be created only when needed."
echo
echo "CONFIG_FILE: $CONFIG_FILE"
echo "APP_BACKUP_DIR: $APP_BACKUP_DIR"
echo "DEFAULT_APP_INSTALL_COMMAND: $DEFAULT_APP_INSTALL_COMMAND"
echo "DEFAULT_APP_BACKUP_TYPE: $DEFAULT_APP_BACKUP_TYPE"
echo "DUMP_DIR: $DUMP_DIR"
echo
if [[ $(promptYesNo "Are you okay with these settings?") -ge 1 ]]; then
	echo "User is okay with these settings."
	echo "Continuing..."
else
	echo "User is not okay with these settings."
	echo "Exiting..."
	exit
fi

# Implementation: Let user choose from:
# manual/automatic install/backup here
# If automatic: Ask user to choose from 'apps', 'archive', or 'both'

runAtEnd

###################
#  END OF SCRIPT  #
# USER INPUT HERE #
###################

# User can remain in script & 
# input extra commands or exit script here.
echo
echo "End of script!"
echo
echo "You can manually run extra commands within the script or type 'exit' to quit."
echo "TO BE IMPLEMENTED: Type 'help' to get help on custom script commands."
while
appInstallBackups=0
read -p ": " userIn
do
	if [ "$userIn" = 'help' ]; then
		echo "Help function should be called..."
	else
		eval $userIn
	fi
done

