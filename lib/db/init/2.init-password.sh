mongosh -- <<EOF
    use admin
    db.changeUserPassword('$MONGO_USER', '$(cat /run/secrets/MONGO_USER_PW)')
EOF