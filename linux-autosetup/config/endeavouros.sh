##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

APP_BACKUP_DIR="../app-backups"

alias yay="sudo -u $SUDO_USER yay"
alias flatpak="sudo -u $SUDO_USER flatpak"

DEFAULT_APP_INSTALL_COMMAND="yay -S --noconfirm $app"

# DUMP_DIR="./dump"

################
# APPLICATIONS #
################

ffProfile="$HOME/.mozilla/firefox/PROFILE"
thProfile="$HOME/.thunderbird/PROFILE"

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"

# Essentials
App firefox "firefox.installBackups" "" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json,search.json.mozlz4} "$ffProfile/storage/default/"
App thunderbird "" "" "$thProfile/"{abook.sqlite,cert9.db,history.sqlite,key4.db,logins.json,prefs.js}
App flatpak
App ffmpeg
App redshift "" "" "$HOME/.config/redshift.conf"

# Extras
App discord "flatpak install com.discordapp.Discord"
App soundux
App quodlibet
App gifski "rust.install && cargo install gifski"
App youtube-dl

# Pipewire setup
App pipewire "$DEFAULT_APP_INSTALL_COMMAND; yay -R pulseaudio-jack; pipewire-pulse.install; systemctl start --user pipewire-pulse.service"
App pipewire-pulse
App easyeffects

# Gaming
App gamemode
App steam
App protonup-git
App lutris

# Gaming - nvidia 1660ti
App nvidia-tdp-1660ti "nvidia-tdp-1660ti.installBackups && systemctl enable nvidia-tdp.timer && systemctl start nvidia-tdp.service; remove-tlp.install" "" "/etc/systemd/system/nvidia-tdp."{service,timer}
App remove-tlp "yay -R tlp"
App gwe #greenwithenvy

# Gaming - peripherals apps
App piper
App g910-gkeys-git "$DEFAULT_APP_INSTALL_COMMAND && g910-gkeys.installBackups && systemctl enable g910-gkeys.service" "" "/etc/g910-gkeys/config.json"
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

# Dependencies
App rust
App linux-headers

# Misc
App clamtk

######################
# APPLICATION GROUPS #
######################

appGroups=(
	[ToBackup]="
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
	[G-main]="
		gamemode
		steam
		lutris
	"
	[G-1660ti]="
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
