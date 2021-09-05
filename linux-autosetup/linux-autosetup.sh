#!/bin/bash

# Default variable fallbacks

# Working directory that script resets to after every install script
# in case installCommand uses cd
declare SCRIPT_WORKING_DIR=$(pwd)
# Where application backups go
declare APP_BACKUP_DIR=./app-backups
# Where recovery files go
declare REC_BACKUP_DIR=./recovery
# Default install command used if one is not specified for app
declare defaultInstallCommand='echo User must set defaultInstallCommand. "name" will not be installed until this is done.'

# Global functions

isEmptyString() {
	if [[ $1 == ' ' || $1 == '|' || $1 == '-' ]]; then
		echo 'true'
	else
		echo ''
	fi
}

# source app and rec class files
. classes/app.h
. classes/rec.h

# Import and source config files
# . applist
. config


app java
java.constructor

