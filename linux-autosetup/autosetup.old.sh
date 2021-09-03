#!/bin/bash

Help() {
	echo "Help hath been displayed."
}

while getopts ":h" option; do
   case $option in
      h) # Help option
         Help
         exit;;
     \?)
         echo "Error: Invalid option"
         exit 1
   esac
done

# Require run as root
if [ $(id -u) -ne 0 ]; then
	echo "Please run as root! Exiting..."
	exit 1
fi

# Ask user whether to copy and install backups or update backup files
echo -n "What do you want to do? 'install' or 'backup': "
read run
if [[ $run != 'install' && $run != 'backup' ]]; then
	echo -n "Input not recognized! Did you spell 'install' or 'backup' incorrectly? Exiting..."
	exit 1
fi

if [ $run = 'install' ]; then
	# Run installer script
	echo -n "Currently not implemented yet. sorry!"
	exit
elif [ $run = 'backup' ]; then
	# Run backuper script
	bash ./applications/linux/backup.sh
else
	echo -n "umm... you're not supposed to be seeing this message in the terminal. what did you do??"
	exit 1
fi

####################################
# BREAK UP INTO SECTIONS OF SETUPS #
# TO RUN DEPENDING ON OPTIONS SET  #
####################################
## setup
# applications
# backups
# firefox - idea: change to be inside 'applications'? idea: only back up bookmarks & extensions?
# thunderbird

## file-backups
# setup
# Files

