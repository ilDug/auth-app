#! /bin/zsh

# ask if the user wants to create the certificates 
echo "Do you want to create the certificates for PRODUCTION? (y/n)"
read CREATE_CERTIFICATES


    # define paths
CERTS=lib/secrets/certs
KEYS=lib/secrets/keys
PATHS=(
    $CERTS
    $KEYS
)
DEST=backend/lib/
CNF=lib/config/openssl/openssl.cnf


 
# check if the user wants to create the certificates
if [ $CREATE_CERTIFICATES = "y" ]; then
    mkdir -p "${PATHS[@]}"

    # create directories
    mkdir -p $CERTS $KEYS

    # create  certificate key pair
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout $KEYS/auth.key -out $CERTS/auth.crt -config $CNF
fi


