#! /bin/zsh

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS

# generate a secret hex key for the MONGO PASSWORD
# The tr command is used to translate or delete characters. 
# In this case, the -d option is used to delete the newline character (\n). 
# This ensures that the generated random string is written to the file without any newline characters.
echo $(openssl rand -hex 32) | tr -d '\n' > $SECRETS/MONGO_ROOT_PW  
echo $(openssl rand -hex 32) | tr -d '\n' > $SECRETS/MONGO_USER_PW 

# generate the email configuration
cat <<EOF > $SECRETS/MAIL_CONFIG
{
    "host": "mail.xxx.com",
    "port": 465,
    "user": "user@xxx.com",
    "password": "xxxxxxxxxxxxx"
}
EOF

