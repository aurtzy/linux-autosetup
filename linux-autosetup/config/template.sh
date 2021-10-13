##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

DEFAULT_APP_INSTALL_COMMAND="echo User must set DEFAULT_APP_INSTALL_COMMAND in configuration file. $app will not be installed until this is done."

ARCHIVE_BACKUP_DIR="./archives"

DEFAULT_ARCHIVE_BACKUP_TYPE="COPY"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################
# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/files/to/backup" "more/files/and/etc"



######################
# APPLICATION GROUPS #
######################

appGroups=(
	[Template]="
		app1
		app2
		app3
	"
)

############
# ARCHIVES #
############
# Archive "archive_name" "backupType:COPY,COMPRESS,ENCRYPT" "path/to/files/to/archive" "more/files/and/etc"



###################
# EVENT FUNCTIONS #
###################
# Completely optional, and do not have to be included 
# (script has fallback defaults which this shows for reference)

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
archiveCompress() {
	tar -cJvPf "$1.tar.xz" "${@:2}"
}
archiveEncrypt() {
	export GPG_TTY=$(tty)
	tar -cJvPf - "${@:2}" | gpg --cipher-algo aes256 --pinentry-mode=loopback --symmetric -o "$1.tar.xz.gpg"
}
archiveDecompress() {
	tar -xJvPf "$1.tar.xz"
}
archiveDecrypt() {
	export GPG_TTY=$(tty)
	gpg --pinentry-mode=loopback -d "$1.tar.xz.gpg" | tar -xJvPf -
}
