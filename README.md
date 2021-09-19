**This is currently in a *beta* state. Features are being wrapped up, and focus is mainly on documentation and bugfixing.**
# Linux Autosetup
Linux Autosetup is a script that uses bash to automate installation and backup processes. Its goal is to be as configurable as possible so that users can customize how and what they want to back up or install.  

## Contents  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Configuration](#configuration)  
  - [Creating a Config File](#creating-a-config-file)  
  - [Configuration Options](#configuration-options)  
  - [Adding Apps](#adding-apps)  
  - [Adding App Groups](#adding-app-groups)  
  - [Function Calls at End of Autosetup](#function-calls-at-end-of-autosetup)
- [Usage](#usage)  
- [Mentions](#mentions)  

# Requirements
- Bash 5.0.17+, which should be present on most modern Linux distributions (Older versions may also work, but this is not guaranteed)
- A Linux distribution

# Installation
Extract the tar and place the linux-autosetup folder wherever you want.  

# Configuration
*This script assumes a working directory where linux-autosetup.sh is located.*  

Configuration files should be found in the ./config directory. The following link contains example config files that are based on lists of apps that I've compiled which you may copy or use as a guideline:  
https://github.com/aurtzy/linux-autosetup/tree/stable/linux-autosetup/config  

## Creating a Config File  
You can make a config file from scratch or copy from one of the examples in the link above.  

Add this config file name to the CONFIG_FILES variable which should be found in ./config/src:  
```
CONFIG_FILES=(  
  "insert_config_file_name_here"
  "add_second_config_file_here_if_desired"
  "etc..."
)
```

## Configuration Options  
Options are completely optional unless otherwise stated.  

This script offers a couple of options that you can customize by changing specific variables:  

- ```DEFAULT_APP_INSTALL_COMMAND``` must be set by the user. It is the default command used for apps that do not have a specified custom install command. ```$app``` can be used to substitute the app name provided, e.g: ```"sudo apt install $app"```  

- ```DEFAULT_APP_BACKUP_TYPE``` uses ```"COPY"``` as a fallback. This is the default backup type used for apps that do not have a specified backup type. See the entry on ```"backup_type"``` in [Adding Apps](#adding-apps) for more information on this option.  

- ```APP_BACKUP_DIR``` uses ```"./app-backups"``` as a fallback. This tells the script where the application backups should be located.  

- ```DUMP_DIR``` uses ```"./dump"``` as a fallback. This tells the script where to dump old backups.  

## Adding Apps
Creating apps simply requires a call to the App function in the config file in the following format:  
```App "appname" "install_command" "backup_type" "directory/to/back/up" "or/file/to/back/up" ...```  

**The only required parameter is ```"appname"```. All other parameters can be omitted or skipped by using empty quotes ```""```**  

Descriptions of the parameters:  

- ```"appname"``` should be the same name used for installing the app (e.g. ```sudo apt install github-desktop``` should use "github-desktop" for appname)  
If a custom install command is used, you can call your appname anything. This should not have spaces.  
- ```"install_command"``` replaces the default install command. If this parameter is not empty, the script will run this command (or commands - you can enter a one-liner with commands separated by semicolons) instead.
- ```"backup_type"``` has two valid options: ```"COPY"``` and ```"HARDLINK"```. ```"COPY"``` uses the traditional method of backing up by copying files, while ```"HARDLINK"``` hard-links files.  
*Note: Hard-linking saves space, but is only recommended if accompanied by additional backups to other sources (e.g. compressing backup folder to secondary drive) as problematic changes to the original files will also affect the backup files.*  
- Every parameter after these are interpreted as backup source paths.  

## Adding App Groups  
App groups are an easy way to organize apps for different use-cases depending on the system. For example, you may want to install gaming and development apps on your main desktop computer, but only want development apps for your laptop - instead of finding and listing all of the apps you want to install every time, you only have to do it once in the config and call the group names.  

App groups are initialized through the following format:
```
appGroups=(
  [AppGroupName]="
    app1
    app2
    app3
  "
  [AnotherAppGroupName]="
    app2
    app4
    app5
  "
)
```  
Notes:  
- App groups are completely optional.  
- Apps are not limited to one app group - you can assign an app to more than one app group  
- App groups are limited to names without spaces and names that do not overlap with app names. The latter can be avoided by capitalizing app group names.  

## Function Calls at End of Autosetup  
/* to-do */

# Usage  
Open a terminal in your linux-autosetup directory and run ```bash linux-autosetup.sh``` with root priviliges.  

The script will prompt you to choose settings for the autosetup to run.  

You can run the command ```bash linux-autosetup.sh -m``` in order to skip the autosetup phase and allow you to enter manual commands if the autosetup does not accomplish what you want. You can read documentation on functions that the ./class/ and linux-autosetup.sh files employ if you wish to directly call them while running in the manual mode.  

## Mentions
Credit to Maxim Norin (https://github.com/mnorin) for their OOP emulation in Bash initially found here: https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
