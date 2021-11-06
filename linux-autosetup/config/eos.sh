# ENDEAVOUROS CONFIG FILE

declare drive2="/run/media/$SUDO_USER/Stuff"
declare driveBackup="/run/media/$SUDO_USER/Backup"

yay="sudo -u $SUDO_USER yay --noconfirm"
flatpak="sudo -u $SUDO_USER flatpak -y --noninteractive"

##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

APP_BACKUP_DIR="$HOME/Backups/apps"

#APP_INSTALL_BACKUPS=1

DEFAULT_APP_INSTALL_COMMAND="$yay -S $app"

ARCHIVE_BACKUP_DIR="../"

DEFAULT_ARCHIVE_BACKUP_TYPE="COMPRESS"

DUMP_DIR="$HOME/DUMP_linux-autosetup"

################
# APPLICATIONS #
################

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"

# Base apps
ffProfile="$HOME/.mozilla/firefox/firefox.al-default"
App firefox "firefox.installBackups" "" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json,search.json.mozlz4} "$ffProfile/storage/default/"
thProfile="$HOME/.thunderbird/thunderbird.al-default"
App thunderbird "" "" "$thProfile/"{abook.sqlite,cert9.db,history.sqlite,key4.db,logins.json,prefs.js,pubring.gpg,revocations.txt,secring.gpg}
App flatpak
App discord "$flatpak install com.discordapp.Discord"
App ffmpeg
App quodlibet
App youtube-dl

# Main desktop apps
 # nvidia
App nvidia-driver "linux-headers.install; nvidia-installer-dkms"
App nvidia-1660ti "nvidia-driver.install; nvidia-1660ti.installBackups && systemctl enable nvidia-tdp.timer && systemctl start nvidia-tdp.service; remove-tlp.install" "" "/etc/systemd/system/nvidia-tdp."{service,timer}
App gwe # greenwithenvy
 # peripherals
App piper
App g910-gkeys-git "$DEFAULT_APP_INSTALL_COMMAND && g910-gkeys.installBackups && systemctl enable g910-gkeys.service" "" "/etc/g910-gkeys/config.json"
App keyboard-center "" "" "$HOME/.config/keyboard-center"
 # etc
App remove-tlp "$yay -R tlp"

# Pipewire
App pipewire "pipewire-pulse.install; systemctl start --user pipewire-pulse.service"
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

# Softwares
 # devving tools
App eclipse-ecj
App intellij-idea-community-edition
App jdk-openjdk
 # video/image editing
App obs-studio
App kdenlive
App losslesscut-bin
App gimp
App krita
App gifski "rust.install && cargo install gifski"
 # misc
App redshift "" "" "$HOME/.config/redshift.conf"
App clamtk

# Dependencies/library stuff
App rust
App linux-headers


######################
# APPLICATION GROUPS #
######################

appGroups=(
	[Base-Apps]="
		firefox
		thunderbird
		flatpak
		discord
		ffmpeg
		quodlibet
		youtube-dl

		pipewire
		easyeffects
	"
	[Main-Desktop-Apps]="
		remove-tlp
		nvidia-1660ti
		Base-Apps
		gifski
		piper
		keyboard-center
		Gaming
	"
	[Gaming]="
		gamemode
		steam
		lutris
		protonup-git
	"
)

############
# ARCHIVES #
############
# Archive "archive_name" "backupType:COPY,COMPRESS,ENCRYPT" "path/to/files/to/archive" "more/files/and/etc"

Archive main-files "ENCRYPT" "$HOME/"{Backups,Workspace}
Archive school "COMPRESS" "$drive2/school"
Archive media "COPY" "$drive2/media" #beeg, no include in archive group

##################
# ARCHIVE GROUPS #
##################

archiveGroups=(
	[Main-Archives]="
		main-files
		school
	"
)

###################
# EVENT FUNCTIONS #
###################

onInstallApps() {
	$yay
}
