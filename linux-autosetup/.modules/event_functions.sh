# FALLBACK EVENT FUNCTIONS

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


# limitation: in order to avoid the wrong archives being dumped, the script requires: .archive to exist after archive name,
# and output path not be messed with excluding extensions that are not .archive
# $1 = output path, $2 = files to archive

archiveCopy() {
	tar -cvPf "$1.tar" "${@:2}"
}

archiveCompress() {
	tar -cJvPf "$1.tar.xz" "${@:2}"
}

archiveEncrypt() {
	export GPG_TTY=$(tty)
	tar -cJvPf - "${@:2}" | gpg --cipher-algo aes256 --pinentry-mode=loopback --symmetric -o "$1.tar.xz.gpg"
}


# $1 = archive path

archiveDecopy() {
	tar -xvPf "$1.tar"
}

archiveDecompress() {
	tar -xJvPf "$1.tar.xz"
}

archiveDecrypt() {
	export GPG_TTY=$(tty)
	gpg --pinentry-mode=loopback -d "$1.tar.xz.gpg" | tar -xJvPf -
}
