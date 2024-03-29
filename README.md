This repository is **no longer active**, and has been superseded by the following projects at the time of writing:
- [git-annex-configure](https://github.com/aurtzy/git-annex-configure), a Guile program that assists with declaratively managing git-annex repositories. This - along with git-annex itself - handles what linux-autosetup attempts to accomplish with backups.
- My [guix-config](https://github.com/aurtzy/guix-config), which utilizes GNU Guix to build a modular configuration system. This project covers the installation aspects of linux-autosetup.

---

# Linux-autosetup
Linux-autosetup is a Bash script that attempts to alleviate and ease installation and backup processes through the use of config files, reducing downtime from pains like forgetting to install apps and backups on fresh installs or backing up files by following crude text documents. It aims to be as configurable as possible so that users can customize how and what they want to back up or install.

# Requirements
- Bash 5.0.17+ (Older versions may also work, but this is not guaranteed)
- A Linux distribution

# Documentation
You can find documentation on how to download and use this script on the [wiki](https://github.com/aurtzy/linux-autosetup/wiki).

#
*Credit to Maxim Norin (https://github.com/mnorin) for their OOP emulation in Bash initially found here: https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277*
