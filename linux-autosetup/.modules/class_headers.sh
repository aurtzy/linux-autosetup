# CLASS HEADERS

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
	checkDuplicateNames "$1"
	fields="app_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/App/$1/g" "$MODULES_DIR"/classes/App.class))
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
	elif [[ "$1" =~ [[:blank:]] ]]; then
		echo
		echo "Error: app group name '$1' has whitespaces"
		echo "App group names cannot have whitespaces (e.g. spaces, tabs)."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
	fi
	checkDuplicateNames "$1" "appGroups"
	fields="appGroup_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/AppGroup/$1/g" "$MODULES_DIR"/classes/AppGroup.class))
	$1.constructor ${@:2}
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
	checkDuplicateNames "$1"
	fields="archive_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/Archive/$1/g" "$MODULES_DIR"/classes/Archive.class))
	$1.constructor "${@:2}"

	archives+=("$1")
}

# Archive group constructor caller
# $1=name
ArchiveGroup() {
	if [ "$1" = '' ]; then
		echo "Error: ArchiveGroup name parameter was empty."
		return
	elif [[ "$1" =~ [[:blank:]] ]]; then
		echo
		echo "Error: Archive group name '$1' has whitespaces"
		echo "Archive group names cannot have whitespaces (e.g. spaces, tabs)."
		echo "Please check your config file and resolve the issue."
		echo "Exiting..."
		exit 1
	fi
	checkDuplicateNames "$1" "archiveGroups"
	fields="archiveGroup_$(convertHyphens "$1")_fields"
	. <(sed "s/fields/$fields/g" <(sed "s/ArchiveGroup/$1/g" "$MODULES_DIR"/classes/ArchiveGroup.class))
	$1.constructor ${@:2}
}

###########
# HELPERS #
###########

# Check for duplicate names and throw error+exit if one is found
checkDuplicateNames() {
	if [ "$2" = "appGroups" ]; then
		if [[ "${apps[*]} ${archives[*]} ${!archiveGroups[*]}" =~ "$1" ]]; then
			echo "Error: $1 has an overlapping name, please fix."
			exit 1
		fi
	elif [ "$2" = "archiveGroups" ]; then
		if [[ "${apps[*]} ${!appGroups[*]} ${archives[*]}" =~ "$1" ]]; then
			echo "Error: $1 has an overlapping name, please fix."
			exit 1
		fi
	else
		if [[ "${apps[*]} ${!appGroups[*]} ${archives[*]} ${!archiveGroups[*]}" =~ "$1" ]]; then
			echo "Error: $1 has an overlapping name, please fix."
			exit 1
		fi
	fi
}

# String converter methods to allow functionality with Bash
# Convert '-' and $hyphenConversion from and to each other
convertHyphens() {
	echo ${1//-/_}
}

