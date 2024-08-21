#! /bin/bash

# Define some colors first
NC='\033[0m' # No Color
RED='\033[1;31m'
GREEN='\033[1;32m'
GREY='\033[1;30m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
AZURE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[0;36m'

# define paths
SECRETS=lib/secrets

# create directories
mkdir -p $SECRETS


# loop until the user enters the user
while true; do
  echo -e "\n${GREY}enter the ${BLUE}username ${GREY} ${NC} "
  read USER

  # check if the username name is not empty
  if [ -z "$USER" ]
  then
    echo -e "${RED}user name cannot be empty${NC}"
  else
    break
  fi
done


# loop until the user enters the database name
while true; do
  echo -e "\n${GREY}enter the ${BLUE}database${GREY} name${NC} "
  read DB

  # check if the database is not empty
  if [ -z "$DB" ]
  then
    echo -e "${RED}database name cannot be empty${NC}"
  else
    break
  fi
done


#  loop until the user enters the hostname
while true; do
  echo -e "\n${GREY}enter the ${BLUE}hostname:ports ${GREY}(e.g. ${PURPLE}localhost:27017${GREY}, OR REPLICA SET: ${PURPLE}mongo1.dag.lan:27017,mongo2.dag.lan:27017,mongo3.dag.lan:27017${GREY})${NC} "
  read HOST

  # check if the hostname is not empty 
    if [ -z "$HOST" ]
    then
        echo -e "${RED}hostname cannot be empty${NC}"
        continue
    fi

    # check if $HOST follow the pattern
    if [[ $HOST =~ ^[a-zA-Z0-9\.\,]+:[0-9]+(,[a-zA-Z0-9\.\,]+:[0-9]+)*$ ]]; then
        echo -e "${GREEN}The MongoDB have the correct format host:port .${NC}"
        break
    else
         echo -e "${RED}hostname must have the format host:port ${NC}"
    fi

done

#  store in a boolean variable if the hostname is a replica set, following the pattern
if [[ $HOST =~ ^[a-zA-Z0-9\.\,]+:[0-9]+,[a-zA-Z0-9\.\,]+:[0-9]+,[a-zA-Z0-9\.\,]+:[0-9]+ ]];
then
  IS_REPLICA_SET=true
else
  IS_REPLICA_SET=false
fi


PW_FILE="$SECRETS/MONGO_${USER}_PW"

# check if MONGO_USER_PW file exists
if [ -f $PW_FILE ]; then
    echo -e "${YELLOW}MongoDB user password already exists.${NC}"
    echo -e "${YELLOW}Do you want to overwrite the password? (y/n)${NC}"
    read OVERWRITE_PW

    if [ $OVERWRITE_PW = "y" ]; then
        echo -e "${GREY}Creating MongoDB user password...${NC}"
        # generate the secrets
        LENGTH=64
        echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $PW_FILE
    else
        echo -e "${GREY}Using the existing MongoDB user password.${NC}"
    fi
else
    echo -e "${GREY}MongoDB user password does not exist. Creating MongoDB user password...${NC}"
    # generate the secrets
    LENGTH=64
    echo $(openssl rand -base64 256) | tr -dc 'a-zA-Z0-9-_' | fold -w $LENGTH | head -n 1 | tr -d '\n' > $PW_FILE
fi

# retrive contetent of MONGO_USER_PW
PW=$(cat $PW_FILE)



# generate the connection string, and store in a variable MONGO_CS
if [ "$IS_REPLICA_SET" = true ]
then
  MONGO_CS="mongodb://$USER:$PW@$HOST/$DB?authSource=admin&replicaSet=rs0"
else
  MONGO_CS="mongodb://$USER:$PW@$HOST/$DB?authSource=admin"
fi


# print the connection string
echo -e "\n${GREEN}generating credentials in  ./${USER}_credentials${NC}\n"

# save the credentials in a file
cat << EOF > ./${SECRETS}/${USER}_credentials
username: 
    $USER

password: 
    $PW

database: 
    $DB

host: 
    $HOST

connection string: 
    $MONGO_CS

commands:
    access_to_shell_cmd:
        ssh mongo1 "docker exec -it mongodb mongosh -u root -p \$(cat /var/mongo/MONGO_ROOT_PW) --authenticationDatabase admin"
    
    create_user_cmd: | 
        use admin

        db.createUser({
            user: "$USER",
            pwd: "$PW",
            roles: [
                { db: "$DB", role: "readWrite" },
                { db: "$DB", role: "dbAdmin" },
            ]
        })

    grant_roles_cmd: |
        db.grantRolesToUser(
            "$USER",
            [
                { db: "$DB", role: "userAdmin" },
                { db: "$DB", role: "dbOwner" }
            ]
        )

    change_pw_cmd: |
        use admin
        db.changeUserPassword("$USER", "$PW")
        db.changeUserPassword("$USER", passwordPrompt())

    authentication_cmd: |
        use $DB
        db.auth("$USER", "$PW")

    drop_user_cmd: |
        use admin
        db.dropUser("$USER")
    
EOF