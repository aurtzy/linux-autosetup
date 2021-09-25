#!/bin/bash

version="v1.0.0-pre_release-1"

# Print information about the script,
# including version # and copyright
# Pass 'less' param to print shortened vers.
printScriptInfo() {
	echo
	echo "Linux-Autosetup, version $version"
	echo "Copyright (C) 2021 Aurtzy"
	if [ "$1" ]; then
		echo
		if [ "$1" = 'more' ]; then
			echo "Use the -h option to see all available options you can run the script with."
			echo
			echo "Linux-Autosetup comes with ABSOLUTELY NO WARRANTY; for details run this script with the -w option. This is free software, and you are welcome to redistribute it under certain conditions; run this script with the -c option for details."
		elif [ "$1" = 'warranty' ]; then
			echo "This program is distributed in the hope that it will be useful, WITHOUT ANY WARRANTY; without even the implied warranty of or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details."
		elif [ "$1" = 'copyright' ]; then
			echo "This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or at your option) any later version."
		elif [ "$1" = 'help' ]; then
			echo "Linux-Autosetup options:"
			echo "	-m		run in manual mode; skip autosetup"
			echo
			echo "	-v		display version"
			echo "	-c		display copyright information"
			echo "	-w		display warranty information"
		fi
	fi
}

# Check for options passed
while getopts ":mhvcw" option; do
	case $option in
		m) skipAutosetup="1"; break;;
		h) printScriptInfo help; exit;;
		v) printScriptInfo; exit;;
		c) printScriptInfo copyright; exit;;
		w) printScriptInfo warranty; exit;;
		\?) echo "Error: Option not recognized."; exit;;
   esac
done

# Force run as root
if [ $(id -u) -ne 0 ]; then
	echo
	echo "This script must be run with root priviliges. Running with sudo..."
	sudo bash "$0" "$@"
	exit $?
fi

####################
# STATIC VARIABLES #
####################

# Overwrite $HOME with sudo user
declare HOME="$(eval echo ~${SUDO_USER})"

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
declare app='$app'

##########################
# CONFIGURABLE VARIABLES #
##########################

# If a command call uses cd, this will allow remaining in proper dir
declare SCRIPT_WORKING_DIR="$(pwd)"
# Default configuration folder
declare CONFIG_FOLDER="./config"
# Where classes are stored
declare CLASSES_DIR="./classes"

# Where application backups go
declare APP_BACKUP_DIR="./app-backups"
# Default app backup type - "COPY", "HARDLINK"
declare DEFAULT_APP_BACKUP_TYPE="COPY"
# Default install command used if one is not specified for app
# $app is substituted for app name
declare DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $app will not be installed until this is done."
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
		
		sudo -u $SUDO_USER mkdir -p "$DUMP_DIR/$dumpName/$i"
		if [ "$?" -ne 0 ]; then
			echo "Elevating permissions for mkdir to work..."
			mkdir -p "$DUMP_DIR/$dumpName/$i"
		fi
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
		echo
		echo "Error: app name parameter was empty"
		echo "App names cannot be empty."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
	elif [[ "$1" =~ [[:blank:]] ]]; then
		echo
		echo "Error: app name '$1' has whitespaces"
		echo "App names cannot have whitespaces (e.g. spaces, tabs)."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
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

# Event functions that are meant to be overwritten in configs
onInstall() {
	return
}
onBackup() {
	return
}
onInstallFinish() {
	return
}
onBackupFinish() {
	return
}

##################
# INITIALIZATION #
##################

# Print basic copyright information
printScriptInfo 'more'

# Assign everything in designated config folder
# to CONFIG_FILES
declare -a CONFIG_FILES=("$CONFIG_FOLDER/"*)

# Choose CONFIG_FILE - if there's only one in the array, then automatically choose
if [ ${#CONFIG_FILES[@]} -gt 1 ]; then
	while true; do
		echo
		echo "Which config file do you want to use?"
		for i in "${!CONFIG_FILES[@]}"; do
			echo "$i ${CONFIG_FILES[$i]##*"/"}"
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

# Import CONFIG_FILE & initialize objects
echo
echo "Initializing objects..."
. "$CONFIG_FILE"
initializeAppGroups
echo "All objects successfully initialized."

# Before starting script, ask user if the variables
# that have been set are okay with them. Then, proceed.
echo
echo "**Please double-check the variables that have been set.**"
echo "**Directories will be created only when needed.**"
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

###############
# SCRIPT BODY #
###############

echo 
if [ "$skipAutosetup" != '1' ]; then
	
	declare AUTOSETUP_TYPE
	while true; do
        read -p "Choose an autosetup type for apps [install/backup]: " userIn
        case $userIn in
        	[Ii]*) AUTOSETUP_TYPE="install"; break;;
        	[Bb]*) AUTOSETUP_TYPE="backup"; break;;
        esac
	done
	
	declare -a setupEntries
	echo
	echo "Your apps:"
	echo " $(apps)"
	echo
	echo "Your app groups:"
	echo " $(appGroups)"
	echo
	echo "Add apps or app groups you want to $AUTOSETUP_TYPE from your config."
	echo "Separate entries with spaces or add one every line."
	echo "Type 'apps' or 'appGroups' to show their respective lists again."
	echo
	echo "Type 'done' to finish adding or 'clear' to clear your entries."
	
	while true
	read -p ": " userIn
	do
		for entry in $userIn; do
			if [[ " ${setupEntries[*]} " =~ " $entry " ]]; then
				echo "$entry has already been entered."
				continue
			fi
			if [[ " ${apps[*]} " =~ " $entry " || " ${!appGroups[*]} " =~ " $entry " ]]; then
				setupEntries+=("$entry")
			elif [ "$entry" = 'apps' ]; then
				echo
				echo "Your apps:"
				echo " $(apps)"
			elif [ "$entry" = 'appGroups' ]; then
				echo
				echo "Your app groups:"
				echo " $(appGroups)"
			elif [ "$entry" = 'done' ]; then
				echo
				echo "Done with the list!"
				break
			elif [ "$entry" = 'clear' ]; then
				setupEntries=()
				echo "Setup entries cleared."
			else
				echo "Error: $entry could not be found"
			fi
		done
		
		if [ "$entry" = 'done' ]; then
			echo
			echo "Please confirm that you want to $AUTOSETUP_TYPE the following:"
			echo
			if [ "$AUTOSETUP_TYPE" = 'install' ]; then
				for entry in "${setupEntries[@]}"; do
					if [[ " ${!appGroups[*]} " =~ " $entry " ]]; then
						echo "$entry: $($entry.apps)"
					else
						echo "$entry"
					fi
				done
			elif [ "$AUTOSETUP_TYPE" = 'backup' ]; then
				for entry in "${setupEntries[@]}"; do
					if [[ " ${!appGroups[*]} " =~ " $entry " ]]; then
						echo "$entry:"
						for app in $($entry.apps); do
							echo "  $app:"
							echo "$($app.sourcePaths)"
						done
					else
						echo "$entry: $($entry.sourcePaths)"
					fi
				done
			fi
			echo
			if [ $(promptYesNo "Script will $AUTOSETUP_TYPE everything above. Is this okay?") -ge 1 ]; then
				break
			else
				echo "User is not okay with this"
				setupEntries=()
				echo "Setup entries cleared."
			fi
		fi
		
		if [ "$entry" = 'apps' ] || [ "$entry" = 'appGroups' ]; then
			continue
		fi
		
		echo
		echo "Your current $AUTOSETUP_TYPE list:"
		if [ "$AUTOSETUP_TYPE" = 'install' ]; then
			for entry in "${setupEntries[@]}"; do
				if [[ " ${!appGroups[*]} " =~ " $entry " ]]; then
					echo "$entry: $($entry.apps)"
				else
					echo "$entry"
				fi
			done
		elif [ "$AUTOSETUP_TYPE" = 'backup' ]; then
			for entry in "${setupEntries[@]}"; do
				if [[ " ${!appGroups[*]} " =~ " $entry " ]]; then
					echo "$entry:"
					for app in $($entry.apps); do
						echo "  $app:"
						echo "$($app.sourcePaths)"
					done
				else
					echo "$entry: $($entry.sourcePaths)"
				fi
			done
		fi
	done
	
	
	echo
	if [ "$AUTOSETUP_TYPE" = "install" ]; then
		echo "Do you want to autofill installing backups?"
		echo "Type 'n' to not do anything. 'y' will autofill yes; '-n' will autofill no."
		declare -i userIn=$(promptYesNo)
		if [ $userIn -eq -1 ]; then
			appInstallBackups=-1
		elif [ $userIn -ge 1 ]; then
			appInstallBackups=1
		fi
		echo
		echo "AUTOSETUP: Running onInstall first..."
		onInstall
		echo
		echo "AUTOSETUP: onInstall completed."
		echo
		echo "AUTOSETUP: Installing apps..."
		for entry in "${setupEntries[@]}"; do
			$entry.install
		done
		appInstallBackups=0
		echo
		echo "AUTOSETUP: Finished autosetup install."
		
		echo
		echo "AUTOSETUP: Running onInstallFinish..."
		onInstallFinish
		echo
		echo "AUTOSETUP: onInstallFinish completed."
		
		echo
		echo "AUTOSETUP: IF ANY APPS FAILED TO INSTALL, THEY WILL BE LISTED BELOW:"
		for app in "${apps[@]}"; do
			if [ "$($app.failedInstall)" -eq 1 ]; then
				echo "$app"
			fi
		done
	elif [ "$AUTOSETUP_TYPE" = "backup" ]; then
		echo "AUTOSETUP: Running onBackup first..."
		onBackup
		echo "AUTOSETUP: onBackup completed."
		
		echo
		echo "AUTOSETUP: Backing up apps..."
		for entry in "${setupEntries[@]}"; do
			$entry.backup
		done
		echo
		echo "AUTOSETUP: Finished autosetup backup."
		
		echo
		echo "AUTOSETUP: Running onBackupFinish..."
		onBackupFinish
		echo
		echo "AUTOSETUP: onBackupFinish completed."
		
		echo
		echo "AUTOSETUP: IF ANY APPS FAILED TO BE BACKED UP, THEY WILL BE LISTED BELOW:"
		for app in "${apps[@]}"; do
			if [ "$($app.failedBackup)" -eq 1 ]; then
				echo "$app:"
				echo "$($app.failedBackupSources)"
			fi
		done
		echo
		echo "AUTOSETUP: Be sure to double check if all files were backed up properly,"
		echo "especially if this is a first-time backup!"
	fi
	echo

	echo "AUTOSETUP: Autosetup finished!"
else
	echo "AUTOSETUP: Skipping autosetup..."
fi

###################
#  END OF SCRIPT  #
# USER INPUT HERE #
###################

# User can remain in script & 
# input extra commands or exit script here.
echo
echo "You can manually run commands within the script or type 'exit' to quit."
echo "Type 'Help' to get help on custom script commands."
while
appInstallBackups=0
read -p ": " userIn
do
	eval $userIn
done

