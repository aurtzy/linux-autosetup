#!/bin/bash

# Default fallback variables if config goes wrong somehow

# where application backups go
declare APP_BACKUP_DIR=./app-backups
# where recovery files go
declare REC_BACKUP_DIR=./recovery
# default install command used if one is not specified for app
declare defaultInstallCommand='echo User must set defaultInstallCommand. "name" will not be installed until this is done.'

# Initial functions
isEmptyString() {
	if [[ $1 == '' || $1 == '|' || $1 == '-' ]]; then
		echo 'true'
	else
		echo ''
	fi
}

# OOP emulation credit to Maxim Norin from https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
# source app and rec class files
. classes/app.h
. classes/rec.h

# Import and source config files
# . applist
. config


app java
java.constructor

