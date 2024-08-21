#! /bin/zsh

# ask if the user wants to create the certificates for DEVELOPMENT
echo "La creazione dei certificati è necessaria solo se si usa l'ambiente di sviluppo DEVELEPMENT."
echo "in ambiente di produzione, i certificati sono generati in automatico alla creazione del container."
echo "Do you want to create the certificates for DEVELOPMENT? (y/n)"
read CREATE_CERTIFICATES

# check if the user wants to create the certificates for DEVELOPMENT
if [ $CREATE_CERTIFICATES = "y" ]; then
    # define paths
    CNF=lib/config/openssl/openssl.cnf
    CERTS=backend/lib/certs
    KEYS=backend/lib/keys

    # create directories
    mkdir -p $CERTS $KEYS

    # create  certificate key pair
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout $KEYS/auth.key -out $CERTS/auth.crt -config $CNF
fi


