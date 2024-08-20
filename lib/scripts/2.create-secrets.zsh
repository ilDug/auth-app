#! /bin/zsh

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS

# generate the secrets
LENGTH=64
echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/MONGO_USER_PW 


# Prompts the user to create a root password and generates it if requested.
# 
# This script asks the user if they want to create a root password. If the user
# responds with 'y', it generates a random password using the openssl command
# and saves it to the specified file path. If the user responds with 'n', it
# skips the password creation and exits the script.
#
# Example usage:
#   $ ./2.create-secrets.zsh
#
# Note: This script assumes that the variables $LENGTH and $SECRETS are defined
# and accessible in the environment where the script is executed.
echo "Do you want to create a root password? (y/n)"
read GENERATE_ROOT_PW
if [ $GENERATE_ROOT_PW = "y" ]; then
    echo "Creating root password..."
    echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/MONGO_ROOT_PW  
else
    echo "Skipping root password creation..."
    exit 0
fi
