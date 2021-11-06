
autosetup-install() {
	getEntries

	if [ "$ENTRIES_ARCHIVES" ]; then
		echo "Beginning install for archives..."
		echo "Running onInstallArchives"
		onInstallArchives
		echo "Installing archives"
		install "${ENTRIES_ARCHIVES[@]}"
		echo "Running onInstallArchivesFinish"
		onInstallArchivesFinish
		echo
		echo "Checking for failed installs"
		for archive in "${archives[@]}"; do
			[ "$($archive.failedInstall)" -eq 0 ] || echo "$archive"
		done
	fi
	echo
	if [ "$ENTRIES_APPS" ]; then
		echo "Beginning install for apps..."
		echo "Running onInstallApps"
		onInstallApps
		echo "Installing apps"
		if ! [ "$APP_INSTALL_BACKUPS" ]; then
			echo "APP_INSTALL_BACKUPS was not set. Would you like to autofill/prompt installing backups?"
			echo "Note that this will replace existing files in the system."
			while true; do
				read -p "[-1/0/1/?]: " userIn
				case "$userIn" in
					"?")
						echo "   -1 = never install backups"
						echo "    0 = prompt to install every backup"
						echo "    1 = always install backups";;
					"-1") APP_INSTALL_BACKUPS="-1"; break;;
					0) APP_INSTALL_BACKUPS="0"; break;;
					1) APP_INSTALL_BACKUPS="1"; break;;
				esac
			done
		fi
		install "${ENTRIES_APPS[@]}"
		echo "Running onInstallAppsFinish"
		onInstallAppsFinish
		echo
		echo "Checking for failed installs"
		for app in "${apps[@]}"; do
			[ "$($app.failedInstall)" -eq 0 ] || echo "$app"
		done
	fi
}

autosetup-backup() {
	getEntries

	if [ "$ENTRIES_APPS" ]; then
		echo "Beginning backup for apps..."
		echo "Running onBackupApps"
		onBackupApps
		echo "Backing up apps"
		backup "${ENTRIES_APPS}"
		echo "Running onBackupAppsFinish"
		onBackupAppsFinish
		echo
		echo "Checking for failed back-ups"
		for appBackup in "${appBackups[@]}"; do
			if [ "$($appBackup.absentBackupSourcesCount)" -gt 0 ]; then
				echo "    $appBackup, missing source(s); any existing $appBackup backups are untouched:"
				echo "$($appBackup.absentBackupSources)"
			elif [ "$($appBackup.failedBackup)" -ne 0 ]; then
				echo "    $appBackup: An error occured while trying to perform backup."
			fi
		done
	fi
	echo
	if [ "$ENTRIES_ARCHIVES" ]; then
		echo "Beginning backup for archives..."
		echo "Running onBackupArchives"
		onBackupArchives
		echo "Creating archives"
		backup "${ENTRIES_ARCHIVES[@]}"
		echo "Running onBackupArchivesFinish"
		onBackupArchivesFinish
		echo
		echo "Checking for failed archives"
		for archive in "${archives[@]}"; do
			if [ "$($archive.absentBackupSourcesCount)" -gt 0 ]; then
				echo "    $archive, missing source(s); existing archives are untouched:"
				echo "$($archive.absentBackupSources)"
			elif [ "$($archive.failedBackup)" -ne 0 ]; then
				echo "    $archive: An error occured while trying to create archive."
			fi
		done
	fi
}

###########
# HELPERS #
###########

# Returns true if $1 is a valid object, false otherwise
isValidEntry() {
	[[ " ${apps[*]} " =~ " $1 " || " ${!appGroups[*]} " =~ " $1 " || " ${archives[*]} " =~ " $1 " || " ${!archiveGroups[*]} " =~ " $1 " ]]
}

# Categorize entries
categorizeEntries() {
	declare -ag ENTRIES_APPS=()
	declare -ag ENTRIES_ARCHIVES=()
	for entry in "${ENTRIES[@]}"; do
		if [[ " ${apps[*]} " =~ " $entry " || " ${!appGroups[*]} " =~ " $entry " ]]; then
			ENTRIES_APPS+=($entry)
		elif [[ " ${archives[*]} " =~ " $entry " || " ${!archiveGroups[*]} " =~ " $entry " ]]; then
			ENTRIES_ARCHIVES+=($entry)
		else
			echo "ERROR: error categorizing entries - $entry does not exist."
			echo "aborting"
			exit
		fi
	done
}

install() {
	for arg in "$@"; do
		$arg.install
	done
}

backup() {
	for arg in "$@"; do
		$arg.backup
	done
}

getEntries() {
	if [ "$ENTRIES" ]; then
		for entry in "${ENTRIES[@]}"; do
			if ! isValidEntry "$entry"; then
				echo "ERROR: $entry does not exist."
				echo "aborting"
				exit 1
			fi
		done
		categorizeEntries
		return
	fi

	echo "Entering entry-getter"
	echo "Type 'help' for more information on how to use this entry-getter."
	declare userIn=""
	while true; do
		read -p ": " userIn
		set -- $userIn
		case "$1" in
			done)
				categorizeEntries
				echo "Please confirm your entry selection:"
				echo "APP ENTRIES:"
				for entry in "${ENTRIES_APPS[@]}"; do
					echo "    $entry"
				done
				echo "ARCHIVE ENTRIES:"
				for entry in "${ENTRIES_ARCHIVES[@]}"; do
					echo "    $entry"
				done
				read -p "[y/n]: " userIn
				case "$userIn" in
					y*) break;;
					*) echo aborting; continue;;
				esac;;
			help)
				echo "    help             Print this help."
				echo
				echo "    show -"
				echo "         entries     List all current entries in the list."
				echo "         apps        List all available apps."
				echo "         archives    List all available archives."
				echo "    info   <entry>   Show information about the specified entry."
				echo
				echo "    done             Finish & finalize entry list."
				echo "    add    <entries> Add entries to the entries list."
				echo "    addAppBackups    Add all apps with backups."
				echo "    remove <entries> Remove entries from the entries list."
				echo "    clear            Clear the entries list.";;
			show)
				case "$2" in
					"") echo "Usage: show [entries, apps, archives]";;
					entries) echo "${ENTRIES[@]}";;
					apps)
						echo "    APPS: "
						echo "${apps[@]}"
						echo "    ONLY APPS W/ BACKUPS:"
						echo "${appBackups[@]}"
						echo "    APP GROUPS:"
						echo "${!appGroups[@]}";;
					archives)
						echo "    ARCHIVES:"
						echo "${archives[@]}"
						echo "    ARCHIVE GROUPS:"
						echo "${!archiveGroups[@]}";;
				esac;;
			info)
				case "$2" in
					"")
						echo "Usage: info <entry>";;
					*)
						if isValidEntry "$2"; then
							$2.info
						else
							echo "$2 does not exist."
						fi;;
				esac;;
			add)
				for toAdd in "${@:2}"; do
					if isValidEntry "$toAdd"; then
						ENTRIES+=("$toAdd")
						echo "Adding $toAdd"
					else
						echo "$toAdd does not exist"
					fi
				done;;
			remove)
				declare -a tempEntries=()
				for entry in "${ENTRIES[@]}"; do
					if [[ " $* " =~ " $entry " ]]; then
						echo "Removing $entry"
						continue
					else
						tempEntries+=("$entry")
					fi
				done
				ENTRIES=("${tempEntries[@]}");;
			clear)
				ENTRIES=()
				echo "Entries cleared";;
			addAppBackups)
				ENTRIES+=("${appBackups[@]}")
				echo "Adding: ${appBackups[@]}";;
			exit) exit;;
			*) echo "$1 command not recognized";;
		esac
	done
}
