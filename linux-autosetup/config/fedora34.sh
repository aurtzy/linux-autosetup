##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

DEFAULT_APP_INSTALL_COMMAND="sudo dnf -y install $app"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################

ffProfile="$HOME/.mozilla/firefox/PROFILE"
thProfile="$HOME/.thunderbird/PROFILE"

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"
# https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data
App firefox "firefox.installBackups" "" "$ffProfile/../profiles.ini" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json,search.json.mozlz4} "$ffProfile/storage/default/"
# http://kb.mozillazine.org/Files_and_folders_in_the_profile_-_Thunderbird
App thunderbird "" "" "$thProfile/../profiles.ini" "$thProfile/"{abook.sqlite,cert9.db,history.sqlite,key4.db,logins.json,prefs.js}
App ffmpeg
App rust
App wine "sudo dnf config-manager --add-repo https://dl.winehq.org/wine-builds/fedora/34/winehq.repo; sudo dnf install winehq-stable; winetricks.install"

App discord "flatpak install com.discordapp.Discord"
App easyeffects "flatpak install flathub com.github.wwmm.easyeffects"
App obs-studio
App gifski "rust.install; cargo install gifski"
App quodlibet
App pavucontrol
App winetricks
App youtube-dl

# Gaming
App gamemode
App steam
App lutris

App piper
App nvidia-tdp-1660ti "nvidia-tdp.installBackups; systemctl enable nvidia-tdp.timer" "" "/etc/systemd/system/nvidia-tdp."{service,timer}

# Dev tools
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
	[Backup]="
		firefox
		thunderbird
		nvidia-tdp-1660ti
	"
	[Essentials]="
		firefox
		thunderbird
		ffmpeg
		wine
	"
	# Gaming
	[All-G]="
		G
		G-1660ti
		G-periph
	"
	[G]="
		gamemode
		steam
		lutris
	"
	[G-1660ti]="
		nvidia-tdp-1660ti
	"
	[G-periph]="
		piper
	"
	[G-saves]=""
	# Laptop
	[Laptop]="
		tlp
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
