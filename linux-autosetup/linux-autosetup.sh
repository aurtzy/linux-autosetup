#!/bin/bash

# Require run as root
#if [ $(id -u) -ne 0 ]; then
#	echo "Please run script as root! Exiting..."
#	exit 1
#fi

#########################
# VARIABLE DECLARATIONS #
#########################

# String used to substitute hyphens in creating custom functions
declare hyphenConversion='1_1'
# String used to substitute for app names
declare name='$name'

# "Booleans": -1=false/no, 0=unset, 1=true/yes
# Whether app backups should also be installed - 0 = always ask
# Should reset to 0 after every user command or appGroup install
declare -i installAppBackups=0

# If a command call uses cd, this will allow remaining in proper dir
declare SCRIPT_WORKING_DIR="$(pwd)"
# Where application backups go
declare APP_BACKUP_DIR="./app-backups"
# Default app backup type - "COPY", "HARDLINK"
declare APP_BACKUP_TYPE="COPY"
# Where archive files go
declare ARCHIVE_BACKUP_DIR="./archive"
# Where to dump files
declare DUMP_DIR="./dump"
# Where classes are stored
declare CLASSES_DIR="./classes"
# Default configiguration file
declare CONFIG_FILE="./autosetup_default.conf"

# Default install command used if one is not specified for app
# $nameSubstitution is substituted for app name
declare DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $name will not be installed until this is done."

# Stores all app names
declare -ag apps

# Stores app groups as keys
# Stores apps separated by spaces as data
declare -Ag appGroups

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
	echo ${1//-/"$hyphenConversion"}
}

# App constructor caller
# $1=name, $2=installCommand, $3=backupType, ${@:4}=sourcePaths
app() {
	if [ "$1" = '' ]; then
		echo "Error: app name parameter was empty."
		return
	fi
	fields="$(convertHyphens "$1")_app_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/app/$1/g" "$CLASSES_DIR"/app.class))
	$1.constructor "$2" "$3" "${@:4}"
	allApps.add "$1"
}
# App group constructor caller
# $1=name
appGroup() {
	if [ "$1" = '' ]; then
		echo "Error: appGroup name parameter was empty."
		return
	fi
	fields="$(convertHyphens "$1")_appGroup_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/appGroup/$1/g" "$CLASSES_DIR"/appGroup.class))
	$1.constructor
}
# Archive files constructor caller
# $1=name, $2=? $3=?
archive() {
	if [ "$1" = '' ]; then
		echo "Error: archive name parameter was empty."
		return
	fi
	fields="$(convertHyphens "$1")_archive_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/archive/$1/g" "$CLASSES_DIR"/archive.class))
	$1.constructor "$2" "$3"
}

# Initialize app groups in appGroups array
initializeAppGroups() {
	for appGroup in $(appGroups); do
		appGroup $appGroup
	done
}

# Return all apps separated by spaces
apps() {
	for app in "${apps[@]}"; do
		echo -n " $app"
	done
	echo
}

# Return all appGroups separated by spaces
appGroups() {
	for appGroup in "${!appGroups[@]}"; do
		echo -n " $appGroup"
	done
	echo
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

###############
# SCRIPT BODY #
###############

# Import config autosetup.conf
. config/autosetup.conf

# Create APP appGroup
appGroup allApps

# Import CONFIG_FILE & initialize stuff
. config/$CONFIG_FILE
initializeAppGroups

# Before starting script, ask user if the variables
# that have been set are okay with them. Then, proceed.
echo
echo "**Please double-check the variables that have been set."
echo "**Directories will be created only when needed."
echo
echo "Script working directory: $SCRIPT_WORKING_DIR"
echo "App backup directory: $APP_BACKUP_DIR"
echo "Archive backup directory: $ARCHIVE_BACKUP_DIR"
echo "Default app installation command: $DEFAULT_APP_INSTALL_COMMAND"
echo "Default app backup type: $DEFAULT_APP_BACKUP_TYPE"
echo "Dump directory: $DUMP_DIR"
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
installAppBackups=0
echo -n ": "
read userIn
do
	if [ "$userIn" = 'help' ]; then
		echo "Help function should be called..."
	else
		eval $userIn
	fi
done

