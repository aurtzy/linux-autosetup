##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

DEFAULT_APP_INSTALL_COMMAND="sudo pacman -S $app || "

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"



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
