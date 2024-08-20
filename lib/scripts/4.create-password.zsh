#!/bin/zsh

# define paths
SECRETS=lib/secrets
# set the length of the password (max 256 characters)
LENGTH=32

# create directories
mkdir -p $SECRETS

#create a password with openssl $LENGTH characters long using base64 encoding
echo $(openssl rand -base64 512) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/APP_SECRET  
