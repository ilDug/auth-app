#! /bin/zsh

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS

# generate the secrets
LENGTH=32
echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/MONGO_ROOT_PW  
echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/MONGO_USER_PW 
