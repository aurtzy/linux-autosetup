# linux-autosetup.conf.sh is always read

# Variables may be set here instead
# but will be overwritten if set in CONFIG_FILE

# Majority of configuration is usually located in CONFIG_FILE
# May be useful to use different conf files
# for different distros

# Set any CONFIG_FILE to choose from here
# If specify only one, then it will automatically be chosen
CONFIG_FILES=(
	"example.conf.sh"
	"template.conf.sh"
)