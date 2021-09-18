**This is currently in a _beta_ state. Features are being wrapped up, and focus is mainly on documentation and bugfixing.**
# Linux AutoSetup
Linux Autosetup is a script that uses bash to automate installation and backup processes. Its goal is to be as configurable as possible so that users can customize how and what they want to back up or install.  

## Requirements
- Bash 5.0.17+ (Older versions may also work, but this is not guaranteed)
- Any Linux distribution

## Installation
Extract the tar and place the linux-autosetup folder wherever you want.  

## Configuration

### Creating a config file
Configuration files should be found in the /INSTALL-LOCATION/linux-autosetup/config directory. The following link contains example config files that are based on lists of apps that I've compiled which you may copy or use as a guideline:  
https://github.com/aurtzy/linux-autosetup/tree/stable/linux-autosetup/config*  

Start off by making a config file from scratch or copying from one of the examples in the link above.  

Add this config file name to the CONFIG_FILES variable which should be found in config/src:  
```
CONFIG_FILES=(  
  "insert_config_file_name_here"
  "add_second_config_file_here_if_desired"
  "etc..."
)
```
### Adding Apps

### Adding App Groups

## Usage
/* to-do */

### Credit to:
Maxim Norin (https://github.com/mnorin), for their OOP emulation in Bash initially found here: https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
