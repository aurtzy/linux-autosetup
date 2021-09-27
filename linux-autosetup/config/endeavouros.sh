##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

APP_BACKUP_DIR="../app-backups"

yay="sudo -u $SUDO_USER yay"
flatpak="sudo -u $SUDO_USER flatpak"

DEFAULT_APP_INSTALL_COMMAND="$yay -S --noconfirm $app"

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
App pipewire "$DEFAULT_APP_INSTALL_COMMAND; $yay -R pulseaudio-jack; pipewire-pulse.install; systemctl start --user pipewire-pulse.service"
App pipewire-pulse
App easyeffects "" "" "$HOME/.config/easyeffects"

# Gaming
App gamemode
App steam
App protonup-git
App lutris "$DEFAULT_APP_INSTALL_COMMAND; pacman -S --needed wine-staging giflib lib32-giflib libpng lib32-libpng libldap lib32-libldap gnutls lib32-gnutls \
mpg123 lib32-mpg123 openal lib32-openal v4l-utils lib32-v4l-utils libpulse lib32-libpulse libgpg-error \
lib32-libgpg-error alsa-plugins lib32-alsa-plugins alsa-lib lib32-alsa-lib libjpeg-turbo lib32-libjpeg-turbo \
sqlite lib32-sqlite libxcomposite lib32-libxcomposite libxinerama lib32-libgcrypt libgcrypt lib32-libxinerama \
ncurses lib32-ncurses opencl-icd-loader lib32-opencl-icd-loader libxslt lib32-libxslt libva lib32-libva gtk3 \
lib32-gtk3 gst-plugins-base-libs lib32-gst-plugins-base-libs vulkan-icd-loader lib32-vulkan-icd-loader"

# Gaming - nvidia 1660ti
App nvidia-driver "$yay nvidia-installer-dkms"
App nvidia-1660ti "nvidia-1660ti.installBackups && systemctl enable nvidia-tdp.timer && systemctl start nvidia-tdp.service; remove-tlp.install" "" "/etc/systemd/system/nvidia-tdp."{service,timer}
App remove-tlp "$yay -R tlp"
App gwe #greenwithenvy

# Gaming - peripherals apps
App piper
App g910-gkeys-git "$DEFAULT_APP_INSTALL_COMMAND && g910-gkeys.installBackups && systemctl enable g910-gkeys.service" "" "/etc/g910-gkeys/config.json"
App keyboard-center "" "" "$HOME/.config/keyboard-center"

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
		nvidia-1660ti
	"
	[Essentials]="
		firefox
		thunderbird
		flatpak
		ffmpeg
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
	[G-periph]="
		piper
		keyboard-center
	"
	[G-All]="
		G-main
		G-periph
		nvidia-1660ti
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
)

onInstall() {
	$yay --useask --nocleanmenu --nodiffmenu --noeditmenu --noupgrademenu
}
onBackup() {
	return
}
onInstallFinish() {
	$yay --noanswerclean --noanswerdiff --noansweredit --noanswerupgrade
}
onBackupFinish() {
	return
}
