
declare drive2="/run/media/$SUDO_USER/Stuff"
declare driveBackup="/run/media/$SUDO_USER/Backup"

##########################
# CONFIGURABLE VARIABLES #
##########################

# DEFAULT_APP_BACKUP_TYPE="COPY"

APP_BACKUP_DIR="$HOME/Backups/applications"

yay="sudo -u $SUDO_USER yay"
flatpak="sudo -u $SUDO_USER flatpak"

DEFAULT_APP_INSTALL_COMMAND="$yay -S --noconfirm $app"

ARCHIVE_BACKUP_DIR="$driveBackup/"

DEFAULT_ARCHIVE_BACKUP_TYPE="COMPRESS"

DUMP_DIR="$HOME/DUMP_linux-autosetup+"

################
# APPLICATIONS #
################

# App "appname" "one-liner custom install command" "backupType:COPY,HARDLINK" "path/to/dir/or/folder/to/backup" "other/path/to/backup"

# Essentials
ffProfile="$HOME/.mozilla/firefox/firefox.al-default"
App firefox "firefox.installBackups" "" "$ffProfile/"{bookmarkbackups,xulstore.json,prefs.js,extensions,containers.json,search.json.mozlz4} "$ffProfile/storage/default/"
thProfile="$HOME/.thunderbird/thunderbird.al-default"
App thunderbird "" "" "$thProfile/"{abook.sqlite,cert9.db,history.sqlite,key4.db,logins.json,prefs.js}
App flatpak
App ffmpeg

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
# 1660ti
App nvidia-driver "$yay nvidia-installer-dkms"
App nvidia-1660ti "nvidia-1660ti.installBackups && systemctl enable nvidia-tdp.timer && systemctl start nvidia-tdp.service; remove-tlp.install" "" "/etc/systemd/system/nvidia-tdp."{service,timer}
App remove-tlp "$yay -R tlp"
App gwe #greenwithenvy

# peripherals
App piper
App g910-gkeys-git "$DEFAULT_APP_INSTALL_COMMAND && g910-gkeys.installBackups && systemctl enable g910-gkeys.service" "" "/etc/g910-gkeys/config.json"
App keyboard-center "" "" "$HOME/.config/keyboard-center"

# Softwares
 # Dev tools
App eclipse-ecj
App intellij-idea-community-edition
App jdk-openjdk
 # Video-making
App obs-studio
App kdenlive
App losslesscut-bin
 # Image-editors
App gimp
App krita

# Misc
App redshift "" "" "$HOME/.config/redshift.conf"
App clamtk
 # Dependencies
App rust
App linux-headers


######################
# APPLICATION GROUPS #
######################

appGroups=(
	[All-Desktop]="
		remove-tlp
		Base-Apps
		Pipewire
		Nvidia-1660ti
		Gaming
	"
	[Base-Apps]="
		firefox
		thunderbird
		flatpak
		ffmpeg
		discord
		quodlibet
	"
	[Extra-Tools]="
		youtube-dl
		gifski
	"
	[Pipewire]="
		pipewire
		easyeffects
	"
	[Gaming]="
		gamemode
		steam
		lutris
		piper
		keyboard-center
	"
	[Nvidia-1660ti]="
		nvidia-driver
		nvidia-1660ti
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

onInstall() {
	$yay --useask --nocleanmenu --nodiffmenu --noeditmenu --noupgrademenu
}
onInstallFinish() {
	$yay --noanswerclean --noanswerdiff --noansweredit --noanswerupgrade
}
