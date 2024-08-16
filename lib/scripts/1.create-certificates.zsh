#! /bin/zsh

# define paths
CNF=lib/config/openssl/openssl.cnf
CERTS=backend/lib/certs
KEYS=backend/lib/keys

# create directories
mkdir -p $CERTS $KEYS

# create  certificate key pair
openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout $KEYS/auth.key -out $CERTS/auth.crt -config $CNF