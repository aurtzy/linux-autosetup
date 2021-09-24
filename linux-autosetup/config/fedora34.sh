##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

DEFAULT_APP_INSTALL_COMMAND="sudo dnf install $app"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################

ffProfile="$HOME/.mozilla/firefox/PROFILE"
thProfile="$HOME/.thunderbird/PROFILE"

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"
# https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data
App firefox "" "" "$ffProfile/../profiles.ini" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json} "$ffProfile/storage/default/"*
App firefoxBackups "firefox.installBackups"
# http://kb.mozillazine.org/Files_and_folders_in_the_profile_-_Thunderbird
App thunderbird "" "" "$thProfile/../profiles.ini" "$thProfile/abook.sqlite" "$thProfile/cert9.db" "$thProfile/history.sqlite" "$thProfile/key4.db" "$thProfile/logins.json" "$thProfile/prefs.js"

App discord "flatpak install com.discordapp.Discord"
App ffmpeg
App easyeffects "flatpak install flathub com.github.wwmm.easyeffects"
App obs-studio
App gifski "cargo.install; cargo install gifski"
App quodlibet
App pavucontrol
App wine "sudo dnf config-manager --add-repo https://dl.winehq.org/wine-builds/fedora/34/winehq.repo; sudo dnf install winehq-stable; winetricks.install"
App winetricks
App youtube-dl

# Gaming
App gamemode
App steam
App lutris
App piper

# Dev tools
App cargo
App eclipse
App github-desktop
App intellij
App openjdk-16-jdk

# DE stuff
App file-roller
App gnome-extensions
App gnome-tweaks

# Misc.
App clamtk
App tlp

######################
# APPLICATION GROUPS #
######################

appGroups=(
	
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
