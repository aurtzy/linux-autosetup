**This is currently in a _beta_ state. Features are being wrapped up, and focus is mainly on documentation and bugfixing.**
# Linux AutoSetup
Linux Autosetup is a script that uses bash to automate installation and backup processes. Its goal is to be as configurable as possible so that users can customize how and what they want to back up or install.
# Requirements
This script has only been tested on Mint and Fedora so far, but any modern Linux distribution with Bash should work just fine, as it is possible to configure installation commands to whatever suits your distro.

Linux Autosetup will require some initial configuration beforehand. As such, some basic knowledge of Bash may be helpful in understanding the syntax behind the config settings - however, I have tried (and will keep trying) to document the workings of the script as thouroughly as possible, both in this readme and an example config so that configuration is as easy as possible.
# Configuration
*https://github.com/aurtzy/linux-autosetup/tree/stable/linux-autosetup/config contains example config files that are based on lists of apps that I've compiled which you may copy or use as a guideline.*
1. After creating a config file or copying over one of the templates from the above link into the config/ directory, update the CONFIG_FILES list variable in the linux-autosetup config file in order to include that new file. See the linux-autosetup example in the above link if you are not sure what it should look like.
2. /* to do */
# Usage
/* to-do */
# Credit to:
Maxim Norin (https://github.com/mnorin), for their OOP emulation in Bash initially found here: https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
