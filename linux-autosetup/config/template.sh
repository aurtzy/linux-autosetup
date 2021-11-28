##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

# APP_INSTALL_BACKUPS=""

DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $app will not be installed until this is done."

# ARCHIVE_BACKUP_DIR="./archives"

# DEFAULT_ARCHIVE_BACKUP_TYPE="COPY"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################
# App "app_name" "install_command" "backup_type:COPY,HARDLINK" "backup_path1" "backup_path2" ...



######################
# APPLICATION GROUPS #
######################

appGroups=(
	[app_group_name1]="
		app1
		app2
		app3
	"
)

############
# ARCHIVES #
############
# Archive "archive_name" "backup_type:COPY,COMPRESS,ENCRYPT" "backup_path1" "backup_path2" ...



##################
# ARCHIVE GROUPS #
##################

archiveGroups=(
	[archive_group_name1]="
		archive1
		archive2
		archive3
	"
)

###################
# EVENT FUNCTIONS #
###################
# Completely optional, and do not have to be included 
# (script has fallback defaults which this shows for reference)

onInstallApps() {
	return
}

onInstallAppsFinish() {
	return
}

onBackupApps() {
	return
}

onBackupAppsFinish() {
	return
}

onInstallArchives() {
	return
}

onInstallArchivesFinish() {
	return
}

onBackupArchives() {
	return
}

onBackupArchivesFinish() {
	return
}

archiveCopy() {
	tar -cPf "$1.tar" "${@:2}"
}

archiveCompress() {
	tar -cJPf "$1.tar.xz" "${@:2}"
}

archiveEncrypt() {
	tar -cJPf - "${@:2}" | openssl enc -e -aes-256-cbc -md sha512 -pbkdf2 -salt -out "$1.tar.xz.enc"
}

archiveDecopy() {
	tar -xPf "$1.tar"
}

archiveDecompress() {
	tar -xPf "$1.tar.xz"
}

archiveDecrypt() {
	openssl enc -d -aes-256-cbc -md sha512 -pbkdf2 -salt -in "$1.tar.xz.enc" | tar -xPf -
}

