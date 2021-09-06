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
# String to detect in appstrings as indication of separate dirs
declare stringSeparator=';;'
# String used to substitute for app names
declare name='/name/'

# Script working directory
# If a command call uses cd, this will allow remaining in proper dir
declare SCRIPT_WORKING_DIR="$(pwd)"
# Where application backups go
declare APP_BACKUP_DIR="./app-backups"
# Where recovery files go
declare RECOVERY_BACKUP_DIR="./recovery"
# Where old backups are dumped
declare DUMP_DIR="./dump/old"
# Where classes are stored
declare CLASSES_DIR="./classes"

# Apps config file
declare APPS_CONFIG_FILE="./apps.conf"

# Default install command used if one is not specified for app
# $nameSubstitution is substituted for app name
declare defaultInstallCommand="echo User must set defaultInstallCommand. $name will not be installed until this is done."

# Stores applications as keys
# Stores "app strings" as data
declare -ag apps

# Stores app groups as keys
# Stores apps separated by spaces as data
declare -ag appGroups

####################
# GLOBAL FUNCTIONS #
####################

# Check if parameter directory is valid
# Echoes 'true' if yes, '' if no
isValidDir() {
	if [ -d "$1" ]; then
		echo 'true'
	else
		echo ''
	fi
}

# Make sure directory is valid; otherwise exit script
requireExistingDir() {
	
	if [ ! $(isValidDir "$1") ]; then
		echo "Error: $1 does not exist."
		echo "Do you want this directory to be created for you?" 
		echo "Type 'yes' to confirm, otherwise, script will exit."
		
		echo -n ": "
		read userIn
		if [[ "$userIn" = 'y' || "$userIn" = 'yes' ]]; then
			echo "#implement Creating directory to: $1"
		else
			echo "Exiting..."
			exit
		fi
	fi
}

# Functions used to construct new objects
# Param $1 = name, additional params come after
app() {
	. <(sed "s/app/$1/g" "$CLASSES_DIR"/app.class)
	$1.constructor "$2" "$3"
}
appGroup() {
	. <(sed "s/appGroup/$1/g" "$CLASSES_DIR"/appGroup.class)
	$1.constructor
}
recovery() {
	. <(sed "s/recovery/$1/g" "$CLASSES_DIR"/recovery.class)
	$1.constructor "$2" "$3"
}

# String converter methods to allow functionality with Bash
# Convert '-' and $hyphenConversion from and to each other
convertHyphens() {
	echo ${1//-/"$hyphenConversion"}
}
convertToHyphens() {
	echo ${1//"$hyphenConversion"/-}
}
# Split app string into parameters for app constructor
# $1 = app string, $2 = field
splitAppString() {
	declare appString=$1
	if [ "$appString" = '' ]; then
		return
	fi
	declare -i appStringField=$2
	if [ $2 -eq 1 ]; then
		appString=${appString#*'"'}
		appString=${appString%%'"'*}
	elif [ $2 -eq 2 ]; then
		appString=${appString%'"'*}
		appString=${appString##*'"'}
	else
		echo "Error: splitAppString() took an invalid field #. Exiting..."
		exit
	fi
	echo $appString
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
	for appGroup in "${appGroups[@]}"; do
		echo -n " $appGroup"
	done
	echo
}

#####################
# END OF FUNCTIONS  #
#                   #
# SCRIPT BODY BELOW #
#####################

# Import options.conf
. options.conf
requireExistingDir "$APP_BACKUP_DIR"
echo "App backup directory set to: $APP_BACKUP_DIR"
requireExistingDir "$RECOVERY_BACKUP_DIR"
echo "Recovery backup directory set to: $RECOVERY_BACKUP_DIR"

# Import apps.conf
# Skip lines that do not need to be parsed
# Detects and assigns apps to groups
while IFS= read -r line; do
	# If line is empty or a comment
	if [[ "$line" = '' || ${line:0:1} = '#' ]]; then
		continue
	fi
	
	if [ "$line" = 'APPLICATIONS' ]; then
		section='APPLICATIONS'
		continue
	elif [ "$line" = 'APPLICATION_GROUPS' ]; then
		section='APPLICATION_GROUPS'
		continue
	fi
	
	if [ "$section" = 'APPLICATIONS' ]; then
		app="$(cut -d ' ' -f 1 <<< "$line ")"
		apps+=($app)
		appstring=$(cut -d ' ' -f 2- <<< "$line ")
		appInstallCommand="$(splitAppString "$appstring" 1)"
		appBackupSources="$(splitAppString "$appstring" 2)"
		if [ "$appInstallCommand" = "$appBackupSources" ]; then
			appBackupSources=''
		fi
		app "$(convertHyphens "$app")" "$appInstallCommand" "$appBackupSources"
	elif [ "$section" = 'APPLICATION_GROUPS' ]; then
		if [ ${line:0:6} = 'group=' ]; then
			appGroup="${line:6}"
			appGroups+=("$appGroup")
			appGroup $(convertHyphens "$appGroup")
		else
			$appGroup.add "$line"
		fi
	fi
	
done < "$APPS_CONFIG_FILE"

# Implementation: Let user choose from:
# manual/automatic install/backup here
# If automatic: Ask user to choose from 'apps', 'recovery', or 'both'

###################
#  END OF SCRIPT  #
# USER INPUT HERE #
###################

# User can remain in script & 
# input extra commands or exit script here.
echo
echo "Script has finished!"
echo "You can manually run extra commands within the script or type 'exit' to quit."
echo "TO BE IMPLEMENTED: Type 'help' to get help on custom script commands."
declare userIn=''
while
echo -n ": "
read userIn
do
	userIn=$(convertHyphens "$userIn")
	
	if [ "$userIn" = 'help' ]; then
		echo "Help function should be called..."
	else
		$userIn
	fi
done

