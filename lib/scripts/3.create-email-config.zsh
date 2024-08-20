#! /bin/zsh

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS

# generate the email configuration
cat <<EOF > $SECRETS/MAIL_CONFIG
{
    "host": "mail.xxx.com",
    "port": 465,
    "user": "user@xxx.com",
    "password": "xxxxxxxxxxxxx"
}
EOF

