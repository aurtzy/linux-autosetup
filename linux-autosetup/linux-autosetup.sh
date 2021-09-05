#!/bin/bash

# Default variable fallbacks

# Working directory that script resets to after every install script
# in case installCommand uses cd
declare SCRIPT_WORKING_DIR=$(pwd)
# Where application backups go
declare APP_BACKUP_DIR=./app-backups
# Where recovery files go
declare REC_BACKUP_DIR=./recovery
# Default install command used if one is not specified for app
declare defaultInstallCommand='echo User must set defaultInstallCommand. "name" will not be installed until this is done.'


# Used in classes to determine
# if a function argument is "empty"
isEmptyString() {
	if [[ $1 == ' ' || $1 == '|' || $1 == '-' ]]; then
		echo 'true'
	else
		echo ''
	fi
}

# Source app and rec class files
. classes/app.h
. classes/rec.h

# Import options.conf
. options.conf


# Used to determine if lines
# in apps files should be skipped.
apps_shouldSkipLine() {
	if [[ $1 = '' || ${1:0:1} = '#' ]]; then
		echo 'true'
	else
		echo ''
	fi
}
# String converter methods to allow functionality with Bash
# Convert from/to '-' & '1_1'
convertFromHyphen() {
	echo ${1//-/1_1}
}

convertToHyphen() {
	echo ${1//1_1/-}
}
# Declare apps associative array
# Stores applications as keys
# Stores any params "app strings" as data
declare -Ag apps
# Declare appGroups associative array
# Stores app groups as keys
# Stores apps as data separated by spaces
declare -Ag appGroups
# Import apps.conf
# Skips lines that do not need to be parsed
# Detects and assigns apps to groups
while IFS= read -r line; do
	if [ $(apps_shouldSkipLine "$line") ]; then
		continue
	fi
	
	if [ "$line" = 'APPLICATIONS' ]; then
		echo "$line is APPLICATIONS."
		section='APPLICATIONS'
		continue
	elif [ "$line" = 'APPLICATION_GROUPS' ]; then
		echo "$line is APPLICATION_GROUPS."
		section='APPLICATION_GROUPS'
		continue
	fi
	
	if [ $section = 'APPLICATIONS' ]; then
		echo $line
		apps[$(convertFromHyphen "$(cut -d ' ' -f 1 <<< "$line ")")]=$(cut -d ' ' -f 2- <<< "$line ")
	elif [ $section = 'APPLICATION_GROUPS' ]; then
		if [ ${line:0:6} = 'group=' ]; then
			appGroup=${line:6}
			continue
		else
			appGroups[$appGroup]+="$line "
			continue
		fi
	fi
	
done < "apps.conf"

# Initialize app objects from apps array
for app in "${!apps[@]}"; do
	app $app
	$app.constructor
done


