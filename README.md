**This is currently in a *beta* state, and focus is mainly targeted on polishing features and bugfixing.**
# Linux Autosetup
Linux Autosetup is a script that uses Bash to semi-automate installing and backing up applications to reduce downtime from pains like forgetting to install some apps (including backups associated with them) or searching for certain files to back up through a crude text document. It aims to be as configurable as possible so that users can customize how and what they want to back up or install.  

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
  - [Manual Commands](#manual-commands)
- [Mentions](#mentions)  

# Requirements
- Bash 5.0.17+ (Older versions may also work, but this is not guaranteed)
- A Linux distribution

# Installation
Extract the tar and place the linux-autosetup folder wherever you want.  

# Configuration
*This script assumes a working directory where linux-autosetup.sh is located.*  

Configuration files should be found in the ./config directory. The following link contains example config files that are based on lists of apps that I've compiled which you may copy or use as a guideline. They may also be helpful to use in understanding what kind of things you can do, particularly the example config:  
https://github.com/aurtzy/linux-autosetup/tree/stable/linux-autosetup/config  

## Creating a Config File  
You can make a config file from scratch or copy from one of the examples in the link above and place it in the config folder. The sections below describe what and how you can add to the config file.  

## Configuration Options  
Options are completely optional unless otherwise stated.  

This script offers a couple of options that you can customize by changing specific variables:  

- ```DEFAULT_APP_INSTALL_COMMAND``` must be set by the user. It is the default command used for apps that do not have a specified custom install command. ```$app``` can be used to substitute the app name provided, e.g: ```"sudo apt install $app"```  

- ```DEFAULT_APP_BACKUP_TYPE``` uses ```"COPY"``` as a fallback. This is the default backup type used for apps that do not have a specified backup type. See the entry on ```"backup_type"``` in [Adding Apps](#adding-apps) for more information on this option.  

- ```APP_BACKUP_DIR``` uses ```"./app-backups"``` as a fallback. This tells the script where the application backups should be located.  

- ```DUMP_DIR``` uses ```"./dump"``` as a fallback. This tells the script where to dump old backups.  

*If there is something you would like to change that is not found in this section (e.g. config directory), you may be able to find it in the CONFIGURABLE VARIABLES section in the main bash script.*  
## Adding Apps
Creating apps simply requires a call to the App function in the config file in the following format:  
```App "appname" "install_command" "backup_type" "directory/to/back/up" "or/file/to/back/up" ...```  

**The only required parameter is ```"appname"```. All other parameters can be omitted or skipped by using empty quotes ```""```**  

Descriptions of the parameters:  

- ```"appname"``` should be the same name used for installing the app (e.g. ```sudo apt install github-desktop``` should use "github-desktop" for appname)  
If a custom install command is used, you can call your appname anything. This should not have spaces.  
- ```"install_command"``` replaces the default install command. If this parameter is not empty, the script will run this command (or commands - you can enter a one-liner with commands separated by semicolons) instead. You can even call other apps present the config by calling appname.install, which may be useful for apps that require certain dependencies. See [Manual Commands](#manual-commands) for more functions you can use.  
- ```"backup_type"``` has two valid options: ```"COPY"``` and ```"HARDLINK"```. ```"COPY"``` uses the traditional method of backing up by copying files, while ```"HARDLINK"``` hard-links files.  
*Note: Hard-linking saves space, but is only recommended if accompanied by additional backups to other sources (e.g. compressing backup folder to secondary drive) as problematic changes to the original files will also affect the backup files.*  
- Every parameter after these are interpreted as backup source paths. You can use ```$HOME``` to substitute for the user home directory; note that ```~/``` will not work.    

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
It's recommended that you have some knowledge in Bash before you attempt to use this.  

This script provides two functions, ```onInstallFinish()``` and ```onBackupFinish()``` that you can overwrite and add commands to if the autosetup does not completely accomplish what you need, which run specifically after the autosetup performs an install or backup, respectively.  

# Usage  
Open a terminal in your linux-autosetup directory and run ```bash linux-autosetup.sh``` with root priviliges.  

The script will prompt you with some settings to choose from, after which it will automatically begin the autosetup based on those settings. It will end with any apps it failed to perform the autosetup on.  

### Manual Commands  
You can run the command ```bash linux-autosetup.sh -m``` in order to skip the autosetup phase into the manual mode, which will interpret input as normal terminal commands - just with all of the functions and configurations loaded from the script. You may want to read through [linux-autosetup.sh](https://github.com/aurtzy/linux-autosetup/blob/stable/linux-autosetup/linux-autosetup.sh) or the [class files](https://github.com/aurtzy/linux-autosetup/tree/stable/linux-autosetup/classes) where some documentation is provided for the functions used.  

Here are some commands that may be of interest:  
- ```App.install``` or ```AppGroup.install``` runs install commands for the apps in question.  
- ```App.installBackups``` installs only the backups from the specified app.  
- ```App.backup``` or ```AppGroup.backup``` perform backups.  

*App and AppGroup are substituted with app and app group names, respectively.*

# Mentions
Credit to Maxim Norin (https://github.com/mnorin) for their OOP emulation in Bash initially found here: https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
