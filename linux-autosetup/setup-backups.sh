#!/bin/bash

# Script parameters:
# $1 = 'backup' or 'install'
# $2 = 'all' or specific app name to set up
setupType=$1
appSelect=$2

# Where backups are stored
backupDir="./backups"
# Where old backups are dumped
oldDir="$HOME/.local/share/Trash/files/backups.old"

# Add app backups here.
# Associative array $apps stores app names as keys.
# Storage contains source file name and directory separated by a space.
# Commas separate different source files.
declare -A apps
apps=(
	['test']="./backups testing,./backups testing2"
	['flex']="$HOME asdfg,$HOME/Setup aaaaa"
	#['easyeffects']=""
	#['g910-gkeys']=""
	#['nvidia']=""
)

# Function that backs up all source files associated with specified application
# Take one parameter: $1 app name
# Copies file from $sourceDir to $backupDir if $sourceDir exists.
backup () {
	local app=$1
	local appString=${apps[$app]}
	
	# Make a backup directory if it doesn't exist
	if [ ! -d "$backupDir/$app" ]; then
		echo "$app: Backup folder not found. Making one..."
		mkdir "$backupDir/$app/"
	fi
	# Run through app string to back up file(s)
	declare -i fileNum=0
	while :
	do
		fileNum+=1
		appFile=$(parseAppString $fileNum "$appString")
		sourceDir=$(parseAppFile 1 "$appFile")
		file=$(parseAppFile 2 "$appFile")
		if [ "$sourceDir" != '' ]; then

			# Check if source and target exist before continuing
			if [ ! -f "$sourceDir/$file" ]; then
				echo "$app: "$sourceDir/$file" not found. Skipping..."
				return
			fi
			if [ ! -d "$backupDir" ]; then
				echo "Error! Target for $app not configured properly or does not exist: $backupDir"
				return
			fi
			
			# Dump any preexisting old backup and replace with new hard link
			dump "$backupDir/$app" "$file"
			echo "$app: Backing up file from $sourceDir ..."
			ln "$sourceDir/$file" "$backupDir/$app"
		else
			break
		fi
	done
}

# Function that automatically backs up all apps from $apps when called.
backupAll () {
	for app in ${!apps[@]}; do
    	backup $app
    done
}

# Function that moves specified file into $oldDir
# Dump $2 file from $1 directory if it exists
dump () {
	fileDir="$1"
	file="$2"
	if [ -f "$fileDir/$file" ]; then
		echo "$app: Dumping $file from $fileDir/..."
		if [ -f "$oldDir/$file" ]; then
			declare -i oldNum=2
			while [ -f $oldDir$oldNum/$file ]
			do
				oldNum+=1
			done
			echo "Existing old backup(s) discovered. Dumping to $oldDir$oldNum..."
			if [ ! -d "$oldDir$oldNum/" ]; then
				mkdir "$oldDir$oldNum/"
			fi
		else
			if [ ! -d "$oldDir/" ]; then
				mkdir "$oldDir/"
			fi
			mv "$fileDir/$file" "$oldDir/"
			return
		fi
	fi
}
# Function that parses $apps element string into an appFile
# Takes parameters $1 field number (which field of string to extract), $2 app complete string
# Return form: "$sourcefile $sourceDir"
parseAppString () {
	echo $(cut -d , -f $1 <<< "$2,")
	
}
# Splits given appFile
# Takes parameters $1 field number (1=sourceDir, 2=file), $2 appFile
parseAppFile () {
	echo $(cut -d ' ' -f $1 <<< "$2")
}

# Check if there were any problems with setupType parameter
if [[ "$setupType" != 'backup' && "$setupType" != 'install' ]]; then
	echo "Setup parameters were not recognized."
	echo "Exiting setup-backups.sh..."
	exit 1
else
	echo "Preparing for $setupType..."
	sleep 1
fi
echo

# Ask if user wants a setup a specific app if appSelection is empty string
if [[ "$appSelect" = '' ]]; then
	echo "Would you like to set up a specific application?"
	echo -n "Enter its name (e.g. easyeffects); otherwise, enter 'all' or press enter to set up all applications: "
	read input
	appSelect="$input"
	echo
fi


# SETUP
# BASED ON PARAMETERS SET
if [ "$setupType" = 'backup' ]; then
	
	# Back up specific apps depending on parameter
	if [[ "$appSelect" = 'all' || "$appSelect" = '' ]]; then
		backupAll
	else
		backup "$appSelect"
	fi
	
elif [ "$setupType" = 'install' ]; then
	echo "not implemented yet. supposed to install backups" 
fi


echo "Script completed. Exiting..."
exit






