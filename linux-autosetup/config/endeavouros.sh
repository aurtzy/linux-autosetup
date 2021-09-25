##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

# APP_BACKUP_DIR="./app-backups"

DEFAULT_APP_INSTALL_COMMAND="yay -S $app"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################

ffProfile="$HOME/.mozilla/firefox/PROFILE"
thProfile="$HOME/.thunderbird/PROFILE"

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"

# Essentials
App firefox "firefox.installBackups" "" "$ffProfile/../profiles.ini" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json,search.json.mozlz4} "$ffProfile/storage/default/"
App thunderbird "" "" "$thProfile/../profiles.ini" "$thProfile/"{abook.sqlite,cert9.db,history.sqlite,key4.db,logins.json,prefs.js}
App flatpak "$DEFAULT_APP_INSTALL_COMMAND; flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo; systemctl reboot"
App ffmpeg
App rust

# Extras
App discord "flatpak install com.discordapp.Discord"
App soundux
App quodlibet
App gifski "cargo.install; cargo install gifski"
App youtube-dl

# Pipewire setup
App pipewire
App easyeffects

# Gaming
App gamemode
App steam
App lutris

# Gaming - nvidia 1660ti
App nvidia-driver "linux-headers.install; pacman -S nvidia-installer-dkms; nvidia-installer-dkms; systemctl reboot"
App nvidia-tdp-1660ti "nvidia-tdp.installBackups; systemctl enable nvidia-tdp.timer" "" "/etc/systemd/system/nvidia-tdp."{service,timer}
App gwe #greenwithenvy

# Gaming - peripherals apps
App piper
App keyboard-center

# Dev tools
App github-desktop-bin
App eclipse-ecj
App intellij-idea-community-edition
App jdk-openjdk

# Content-creation - Video making
App obs-studio
App kdenlive
App losslesscut-bin

# Content-creation - Image editors
App gimp
App krita

# Helpers
App linux-headers

# Misc
App clamtk

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
		flatpak
		ffmpeg
		rust
	"
	[Extras]="
		discord
		quodlibet
		gifski
		youtube-dl
	"
	[Pipewire]="
		pipewire
		easyeffects
	"
	[G]="
		gamemode
		steam
		lutris
	"
	[G-1660ti]="
		nvidia-driver
		nvidia-tdp-1660ti
	"
	[G-periph]="
		piper
		keyboard-center
	"
	[G-All]="
		G
		G-1660ti
		G-periph
	"
	[Dev]="
		github-desktop-bin
		intellij-idea-community-edition
		jdk-openjdk
	"
	[C-Video]="
		obs-studio
		kdenlive
		losslesscut-bin
	"
	[C-Image]="
		gimp
		krita
	"
	[Security]="
		clamtk
	"
)

onInstall() {
	yay
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
