#!/bin/bash

version="v1.1.0-beta"

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
			echo "Linux-Autosetup comes with ABSOLUTELY NO WARRANTY; for details type 'show w'. This is free software, and you are welcome to redistribute it under certain conditions; type 'show c' for details."
		elif [ "$1" = 'warranty' ]; then
			echo "This program is distributed in the hope that it will be useful, WITHOUT ANY WARRANTY; without even the implied warranty of or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details."
		elif [ "$1" = 'copyright' ]; then
			echo "This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or at your option) any later version."
		elif [ "$1" = 'help' ]; then
			echo 'to-be-documented...'
		fi
	fi
}

# Force run as root
if [ $(id -u) -ne 0 ]; then
	echo
	echo "This script must be run with root priviliges. Running as sudo..."
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
# Stores all apps with backups
declare -ag appBackups
# Stores app groups as keys
# Stores apps separated by spaces as data
declare -Ag appGroups
# String used to substitute app names
declare app='$app'
# "Booleans": -1=false/no, 0=unset, 1=true/yes
# Whether app backups should also be installed - 0 = always ask
# Should reset to 0 after every user command or AppGroup install
declare -i appInstallBackups=0

# Stores all archives
declare -ag archives
# Stores all archives
declare -Ag archiveGroups

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
# Where archives go
declare ARCHIVE_BACKUP_DIR="./archives"
# Default archive type - "COPY, COMPRESS, ENCRYPT"
declare DEFAULT_ARCHIVE_BACKUP_TYPE="COPY"
# Where to dump files
declare DUMP_DIR="./dump"

#############
# FUNCTIONS #
#############

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
	$1.constructor "${@:2}"
	
	apps+=("$1")
	for arg in "${@:4}"; do
		if [ "$arg" ]; then
			appBackups+=("$1")
			break
		fi
	done
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
# Archive constructor caller
Archive() {
	if [ "$1" = '' ]; then
		echo
		echo "Error: Archive name parameter was empty"
		echo "Archive names cannot be empty."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
	elif [[ "$1" =~ [[:blank:]] ]]; then
		echo
		echo "Error: Archive name '$1' has whitespaces"
		echo "Archive names cannot have whitespaces (e.g. spaces, tabs)."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
	fi
	fields="archive_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/Archive/$1/g" "$CLASSES_DIR"/Archive.class))
	$1.constructor "${@:2}"
	
	archives+=("$1")
}
# Archive group constructor caller
# $1=name
ArchiveGroup() {
	if [ "$1" = '' ]; then
		echo "Error: ArchiveGroup name parameter was empty."
		return
	fi
	fields="archiveGroup_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/ArchiveGroup/$1/g" "$CLASSES_DIR"/ArchiveGroup.class))
	$1.constructor ${@:2}
}
# Initialize archive groups in archiveGroups array
initializeArchiveGroups() {
	for archiveGroup in $(archiveGroups); do
		ArchiveGroup $archiveGroup "${archiveGroups[$archiveGroup]}"
	done
}

# Return all apps
apps() {
	echo "${apps[*]}"
}
# Return all appGroups
appGroups() {
	echo "${!appGroups[*]}"
}
# Return all apps with backups
appBackups() {
	for appBackup in "${appBackups[@]}"; do 
		$appBackup.displayBackups
	done
}
# Return all archives
archives() {
	echo "${archives[*]}"
}
# Return all archives including their backups
archiveBackups() {
	for archive in "${archives[@]}"; do
		$archive.displayBackups
	done
}
archiveGroups() {
	echo "${!archiveGroups[*]}"
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

# Autosetup installer function for apps
app_install() {
	if [ "$1" = "" ]; then
		echo "Your apps:"
		apps
		echo
		echo "Your app groups:"
		appGroups
		echo
		echo "Use this function by running it with the apps you want to install as parameters."
		return
	fi
	for entry in "$@"; do 
		if ! [[ " ${apps[*]} " =~ " $entry " || " ${!appGroups[*]} " =~ " $entry " ]]; then
			echo "Error: $entry could not be found. Perhaps it was spelled incorrectly or does not exist?"
			return 1
		fi
	done
	echo "Please confirm you want to install the following:"
	for entry in "$@"; do 
		echo " $($entry.display)"
	done
	if [ ! $(promptYesNo "Does this look alright?") -ge 1 ]; then
		echo "Aborting"
		return
	fi
	echo "Do you want to autofill installing backups?"
	echo "Type 'n' to prompt for installing backups. 'y' will autofill yes; '-n' will autofill no."
	declare -i userIn=$(promptYesNo)
	if [ $userIn -eq -1 ]; then
		appInstallBackups=-1
	elif [ $userIn -ge 1 ]; then
		appInstallBackups=1
	fi
	echo
	echo "AUTOSETUP: Running onInstall first..."
	onInstall
	echo "AUTOSETUP: onInstall completed."
	echo
	echo "AUTOSETUP: Installing apps..."
	for entry in "$@"; do
		$entry.install
	done
	appInstallBackups=0
	echo
	echo "AUTOSETUP: Finished autosetup install."
	echo
	echo "AUTOSETUP: Running onInstallFinish..."
	onInstallFinish
	echo "AUTOSETUP: onInstallFinish completed."
	echo
	echo "AUTOSETUP: IF ANY APPS FAILED TO INSTALL, THEY WILL BE LISTED BELOW:"
	for app in "${apps[@]}"; do
		if [ "$($app.failedInstall)" -eq 1 ]; then
			echo "$app"
		fi
	done
	echo
	echo "Installation completed."
}

# Autosetup back-uper function for apps
app_backup() {
	if [ "$1" = "" ]; then
		echo "Your app backups:"
		appBackups
		echo
		echo "Your app groups:"
		appGroups
		echo
		echo "Use this function by running it with the apps you want to back up as parameters."
		echo "If you want to back up everything, pass the parameter 'ALL'."
		return
	fi
	declare -a entries=("$@")
	for entry in "${entries[@]}"; do 
		if [ "$entry" = 'ALL' ]; then
			entries=("${appBackups[@]}")
			break
		elif ! [[ " ${appBackups[*]} " =~ " $entry " || " ${!appGroups[*]} " =~ " $entry " ]]; then
			echo "Error: $entry could not be found. Perhaps it was spelled incorrectly or does not exist?"
			return 1
		fi
	done
	echo "Please confirm that you want to back up the following:"
	for entry in "${entries[@]}"; do 
		echo " $($entry.displayBackups)"
	done
	if [ ! $(promptYesNo "Does this look alright?") -ge 1 ]; then
		echo "Aborting"
		return
	fi
	echo
	echo "AUTOSETUP: Running onBackup first..."
	onBackup
	echo "AUTOSETUP: onBackup completed."
	echo
	echo "AUTOSETUP: Backing up apps..."
	for entry in "${entries[@]}"; do
		$entry.backup
	done
	echo
	echo "AUTOSETUP: Finished autosetup backup."
	echo
	echo "AUTOSETUP: Running onBackupFinish..."
	onBackupFinish
	echo "AUTOSETUP: onBackupFinish completed."
	echo
	echo "AUTOSETUP: IF ANY APPS FAILED TO BE BACKED UP, THEY WILL BE LISTED BELOW:"
	for appBackup in "${appBackups[@]}"; do
		if [ "$($appBackup.failedBackup)" -eq 1 ]; then
			echo " $appBackup:"
			echo "$($appBackup.failedBackupSources)"
		fi
	done
	echo
	echo "Be sure to double check if all files were backed up properly,"
	echo "especially if this is a first-time backup!"
	echo
	echo "Backup completed."
}

# Autosetup install archives
archive_install() {
	if [ "$1" = "" ]; then
		echo "Your archives:"
		archiveBackups
		echo
		echo "Your archive groups:"
		archiveGroups
		echo
		echo "Use this function by running it with the apps you want to install as parameters."
		return
	fi
	for entry in "$@"; do 
		if ! [[ " ${archives[*]} " =~ " $entry " ]]; then
			echo "Error: $entry could not be found. Perhaps it was spelled incorrectly or does not exist?"
			return 1
		fi
	done
	echo "Please confirm you want to install the following:"
	for entry in "$@"; do 
		echo " $($entry.displayBackups)"
	done
	if [ ! $(promptYesNo "Does this look alright?") -ge 1 ]; then
		echo "Aborting"
		return
	fi
	echo
	echo "AUTOSETUP: Running onArchiveInstall first..."
	onArchiveInstall
	echo "AUTOSETUP: onArchiveInstall completed."
	echo
	echo "AUTOSETUP: Installing archives..."
	for entry in "$@"; do
		$entry.install
	done
	echo
	echo "AUTOSETUP: Finished autosetup install."
	echo
	echo "AUTOSETUP: Running onArchiveInstallFinish..."
	onArchiveInstallFinish
	echo "AUTOSETUP: onArchiveInstallFinish completed."
	echo
	echo "AUTOSETUP: IF ANY ARCHIVES FAILED TO BE INSTALLED, THEY WILL BE LISTED BELOW:"
	for archive in "${archives[@]}"; do
		[ "$($archive.failedInstall)" -e 0 ] || echo "$archive"
	done
	echo
	echo "AUTOSETUP: Installation completed."
}

# Autosetup create new archives
archive_backup() {
	if [ "$1" = "" ]; then
		echo "Your archives:"
		archiveBackups
		echo
		echo "Your archive groups:"
		archiveGroups
		echo
		echo "Use this function by running it with the apps you want to back up as parameters."
		echo "If you want to archive everything, pass the parameter 'ALL'."
		return
	fi
	declare -a entries=("$@")
	for entry in "${entries[@]}"; do 
		if [ "$entry" = 'ALL' ]; then
			entries=("${archives[@]}")
			break
		elif ! [[ " ${archives[*]} " =~ " $entry " || " ${!archiveGroups[*]} " =~ " $entry " ]]; then
			echo "Error: $entry could not be found. Perhaps it was spelled incorrectly or does not exist?"
			return 1
		fi
	done
	echo "Please confirm you want to back up the following:"
	for entry in "${entries[@]}"; do 
		echo " $($entry.displayBackups)"
	done
	if [ ! $(promptYesNo "Does this look alright?") -ge 1 ]; then
		echo "Aborting"
		return
	fi
	echo
	echo "AUTOSETUP: Running onArchiveBackup first..."
	onArchiveBackup
	echo "AUTOSETUP: onArchiveBackup completed."
	echo
	echo "AUTOSETUP: Backing up archives..."
	for entry in "${entries[@]}"; do
		$entry.backup
	done
	echo
	echo "AUTOSETUP: Finished autosetup backup."
	
	echo
	echo "AUTOSETUP: Running onArchiveBackupFinish..."
	onArchiveBackupFinish
	echo "AUTOSETUP: onArchiveBackupFinish completed."
	echo
	echo "AUTOSETUP: IF ANYTHING FAILED TO BE ARCHIVED, THEY WILL BE LISTED BELOW:"
	for archive in "${archives[@]}"; do
		if [ "$($archive.absentBackupSourcesCount)" -gt 0 ]; then
			echo " $archive:"
			echo "$($archive.absentBackupSources)"
		elif [ "$($archive.failedBackup)" -ne 0 ]; then
			echo " $archive was not archived at all"
		fi
	done
	echo
	echo "Be sure to double check if all files were archived properly,"
	echo "especially if this is a first-time backup!"
	echo
	echo "AUTOSETUP: Backup completed."
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
onArchiveInstall() {
	return
}
onArchiveBackup() {
	return
}
onArchiveInstallFinish() {
	return
}
onArchiveBackupFinish() {
	return
}
# limitation: in order to avoid the wrong archives being dumped, the script requires: .archive to exist after archive name,
# and output path not be messed with excluding extensions that are not .archive
# $1 = output path, $2 = files to archive
archiveCompress() {
	tar -cJvPf "$1.tar.xz" "${@:2}"
}
archiveEncrypt() {
	export GPG_TTY=$(tty)
	tar -cJvPf - "${@:2}" | gpg --cipher-algo aes256 --pinentry-mode=loopback --symmetric -o "$1.tar.xz.gpg"
}
# $1 = archive path
archiveDecompress() {
	tar -xJvPf "$1.tar.xz"
}
archiveDecrypt() {
	export GPG_TTY=$(tty)
	gpg --pinentry-mode=loopback -d "$1.tar.xz.gpg" | tar -xJvPf -
}

##################
# INITIALIZATION #
##################

# Print basic copyright information
printScriptInfo 'more'

# Assign everything in designated config folder
# to CONFIG_FILES, excluding directories
declare -a CONFIG_FILES
for FILE in "$CONFIG_FOLDER/"* ; do 
	if [ -f "$FILE" ]; then
		CONFIG_FILES+=("$FILE")
	fi
done

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
initializeArchiveGroups
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
echo "ARCHIVE_BACKUP_DIR: $ARCHIVE_BACKUP_DIR"
echo "DEFAULT_ARCHIVE_BACKUP_TYPE: $DEFAULT_ARCHIVE_BACKUP_TYPE"
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

##############
# USER INPUT #
##############

# User can remain in script & 
# input extra commands or exit script here.
echo
echo "You can manually run commands within the script or type 'exit' to quit."
echo "Type 'Help' to get help on custom script commands."
while
appInstallBackups=0
read -p ": " userIn
do
	case $userIn in
		"Help") printScriptInfo help; continue;;
		"show c") printScriptInfo copyright; continue;;
		"show w") printScriptInfo warranty; continue;;
	esac
	eval $userIn
done

