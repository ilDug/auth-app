#!/bin/zsh

#create a password with openssl 21 characters long using base64 encoding
echo $(openssl rand -base64 21) | tr -d '\n' > lib/secrets/APP_SECRET