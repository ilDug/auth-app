#! /bin/zsh

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS

# ask for mongodb user name
echo "Enter the MongoDB user name:"
read MONGO_USER_NAME

# check if the user name is empty
if [ -z $MONGO_USER_NAME ]; then
    echo "The MongoDB user name cannot be empty."
    exit 1
fi

# check if MONGO_USER_PW file exists
if [ ! -f $SECRETS/MONGO_USER_PW ]; then
    echo "MongoDB user password does not exists. Creating MongoDB user password..."
    # generate the secrets
    LENGTH=64
    echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $SECRETS/MONGO_USER_PW
fi

# retrive contetent of MONGO_USER_PW
MONGO_USER_PW=$(cat $SECRETS/MONGO_USER_PW)

# ask for mongodb host
echo "Enter the MongoDB host: (e.g. localhost:27017,  OR REPLICA SET: mongo1.dag.lan:27017,mongo2.dag.lan:27017,mongo3.dag.lan:27017)"
read MONGO_HOST

# check if the host is empty
if [ -z $MONGO_HOST ]; then
    echo "The MongoDB host cannot be empty."
    exit 1
fi

# check if $MONGO_HOST follow the pattern
if [[ $MONGO_HOST =~ ^[a-zA-Z0-9\.\,]+:[0-9]+(,[a-zA-Z0-9\.\,]+:[0-9]+)*$ ]]; then
    echo "The MongoDB host is valid."
else
    echo "The MongoDB host is invalid."
    exit 1
fi

# check if MONGO_HOST is a replica set,  at least 3 nodes. then save into a boolean variable IS_RELICA_SET
if [[ $MONGO_HOST =~ ^[a-zA-Z0-9\.\,]+:[0-9]+,[a-zA-Z0-9\.\,]+:[0-9]+,[a-zA-Z0-9\.\,]+:[0-9]+ ]]; then
    IS_RELICA_SET=true
else
    IS_RELICA_SET=false
fi

# ask for mongodb database
echo "Enter the MongoDB database:"
read MONGO_DB

# check if the database is empty
if [ -z $MONGO_DB ]; then
    echo "The MongoDB database cannot be empty."
    exit 1
fi


# build the connection string,  based on IS_RELICA_SET
if [ $IS_RELICA_SET = true ]; then
    MONGO_CONNECTION_STRING="mongodb://$MONGO_USER_NAME:$MONGO_USER_PW@$MONGO_HOST/$MONGO_DB?authSource=admin&replicaSet=rs0"
else
    MONGO_CONNECTION_STRING="mongodb://$MONGO_USER_NAME:$MONGO_USER_PW@$MONGO_HOST/$MONGO_DB?authSource=admin"
fi


# print the connection string
echo "The MongoDB connection string is:"
echo $MONGO_CONNECTION_STRING
echo "check the connection string in the file $SECRETS/MONGO_CS"

# save the connection string to a file
echo $MONGO_CONNECTION_STRING > $SECRETS/MONGO_CS

#create a javascript file named "add-user-and-db.temp.js" to add a user to the database.
cat <<EOF > $SECRETS/add-user-and-db.TEMP.js
admin = db.getSiblingDB("admin")
admin.createUser({ 
    user: "$MONGO_USER_NAME", 
    pwd: "$MONGO_USER_PW", 
    roles: [ 
        { role: "readWrite", db: "$MONGO_DB" } ,
        { role: "dbAdmin", db: "$MONGO_DB" }
    ] 
}) 
EOF

