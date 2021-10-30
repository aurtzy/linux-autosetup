# Initialize user config file
# Skips if CONFIG_FILE is empty

if ! [ "$CONFIG_FILE" ]; then
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

# deprecated
	# Before starting script, ask user if the variables
	# that have been set are okay with them. Then, proceed.
# 	echo
# 	echo "**Please make sure that the following variables have been set to your liking.**"
# 	echo
# 	echo "CONFIG_FILE: $CONFIG_FILE"
# 	echo "APP_BACKUP_DIR: $APP_BACKUP_DIR"
# 	echo "DEFAULT_APP_INSTALL_COMMAND: $DEFAULT_APP_INSTALL_COMMAND"
# 	echo "DEFAULT_APP_BACKUP_TYPE: $DEFAULT_APP_BACKUP_TYPE"
# 	echo "ARCHIVE_BACKUP_DIR: $ARCHIVE_BACKUP_DIR"
# 	echo "DEFAULT_ARCHIVE_BACKUP_TYPE: $DEFAULT_ARCHIVE_BACKUP_TYPE"
# 	echo "DUMP_DIR: $DUMP_DIR"
# 	echo
# 	if [[ $(promptYesNo "Are you okay with these settings?") -ge 1 ]]; then
# 		echo "User is okay with these settings."
# 		echo "Continuing..."
# 	else
# 		echo "User is not okay with these settings."
# 		echo "Exiting..."
# 		exit
# 	fi
elif [[ ! "$CONFIG_FILE" = */* ]]; then
	# LIMITATION: this doesn't work if file is inside work dir since is CONFIG_FOLDER takes precedence when lacking "/"
	CONFIG_FILE="$CONFIG_FOLDER/$CONFIG_FILE"
fi

echo "Loading $CONFIG_FILE"
	. "$CONFIG_FILE"

# Initialize app groups in appGroups array
for appGroup in "${!appGroups[@]}"; do
	AppGroup $appGroup "${appGroups[$appGroup]}"
done

# Initialize archive groups in archiveGroups array
for archiveGroup in "${!archiveGroups[@]}"; do
	ArchiveGroup $archiveGroup "${archiveGroups[$archiveGroup]}"
done
