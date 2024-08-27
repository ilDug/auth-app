#!/bin/zsh

# It builds and pushes a Docker image using buildx, creates a destination folder for the project on the remote host, copies the docker-compose file and the lib folder to the remote host, pulls the latest image, and starts the service using docker-compose.


# Description: 
# This script sets the shell options and defines traps for error handling and exit codes.
# Note:
# - The script uses the 'set -e' option to exit immediately if any command exits with a non-zero status.
# - The 'trap' command is used to define actions to be taken when certain signals are received.
# - The 'DEBUG' signal is trapped to display an error message when an error occurs.
# - The 'EXIT' signal is trapped to display the exit code when the script exits.
set -e
trap 'echo -e "${RED}An error occurred. Exiting...${NC}"' ERR
trap 'echo -e "${BLUE} EXIT CODE $? ${NC}"' EXIT



# Define some colors first
NC='\033[0m' # No Color
RED='\033[1;31m'
GREEN='\033[1;32m'
GREY='\033[1;30m'
LIGHT_GREY='\033[0;37m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
AZURE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[0;36m'


# define image name
IMAGE=cr.dag.lan/auth-backend # the name of the image to be built and pushed
DOCKER_HOST=docker1 # the remote host where the project will be run
PROJECT_PATH=/docker/auth-app # path on the remote host where the project will be run


# ask if execute as dry run
echo -e "${GREY}Do you want to ${GREEN}execute [Y]${GREY} the program or  ${RED}dry-run [N]${GREY} it? (Y/n)${NC}"
echo -e "${GREY}This will only show the commands that will be executed without actually running them.${NC}"
read -r DRY_RUN
echo -e "\n"




# spiega all'utente che il processo di CI/CD è iniziato e verrà creata un immagine di STAGE per il backend che verrà caricata su Docker Registry locale
echo -e "${GREY}CI/CD process started...${NC}"
echo -e "${GREY}Creating a STAGE image ${RED}$IMAGE${GREY} for the backend...${NC}"
echo -e "${LIGHT_GREY}docker buildx build . --file ./Dockerfile.prod.api --tag ${IMAGE}:latest --platform linux/amd64,linux/arm64 --push${NC}\n"

# Build and push a Docker image using buildx
#
# This script builds a Docker image using the buildx command. It specifies the Dockerfile to use, sets the tag for the image, and specifies the platforms to build for. The `--push` flag is used to push the image to a remote registry. The `--no-cache` flag is used to disable caching during the build process.
if [[ $DRY_RUN == "y" ]]; then
    docker buildx build . --file ./Dockerfile.prod.api --tag ${IMAGE}:latest --platform linux/amd64,linux/arm64 --push   
    echo -e "${GREY}Image ${RED}$IMAGE${GREY} has been successfully uploaded to the local Docker Registry${NC}\n"
fi

# spiega all'utente che l'immagine è stata caricata con successo sul Docker Registry locale


# crea la cartella di destinazione del progetto (se non esiste)
echo -e "${GREY}Creating a ${CYAN}destination folder${GREY}for the project on the remote host...${NC}"
echo -e "${LIGHT_GREY}ssh root@$DOCKER_HOST \"mkdir -p $PROJECT_PATH\"${NC}\n"
if [[ $DRY_RUN == "y" ]]; then
    ssh root@$DOCKER_HOST "mkdir -p $PROJECT_PATH"
fi


# copia il file docker-compose.yml nella cartella di destinazione (using rsync)
echo -e "${GREY}Copying the ${BLUE}docker-compose file${GREY} to the remote host...${NC}"
echo -e "${LIGHT_GREY}rsync -avh  ./docker-compose.stage.yaml root@$DOCKER_HOST:$PROJECT_PATH/docker-compose.yaml${NC}\n"
if [[ $DRY_RUN == "y" ]]; then
    rsync -avh --delete ./docker-compose.stage.yaml root@$DOCKER_HOST:$PROJECT_PATH/docker-compose.yaml
fi

# copia la cartella lib nella cartella di destinazione (using rsync)
echo -e "${GREY}Copying the ${PURPLE}lib folder${GREY} to the remote host...${NC}"
echo -e "${LIGHT_GREY}rsync -avh   ./lib root@$DOCKER_HOST:$PROJECT_PATH${NC}\n"
if [[ $DRY_RUN == "y" ]]; then
    rsync -avh --delete ./lib root@$DOCKER_HOST:$PROJECT_PATH
fi

# pull the latest image on the remote host
echo -e "${GREY}Pulling the latest image on the remote host...${NC}"
echo -e "${LIGHT_GREY}docker pull ${IMAGE}:latest${NC}\n"
if [[ $DRY_RUN == "y" ]]; then
    ssh root@$DOCKER_HOST "docker pull ${IMAGE}:latest"
    echo -e "${GREEN}Image ${YELLOW}$IMAGE${GREEN} has been successfully pulled on the remote host${NC}\n"
fi

# esegue il comando docker-compose up -d per avviare il servizio
echo -e "${GREY}Starting the service using ${YELLOW}docker compose up -d${GREY}...${NC}"
echo -e "${LIGHT_GREY}ssh root@$DOCKER_HOST \"cd $PROJECT_PATH && docker compose up -d --force-recreate --remove-orphans --pull always\"${NC}\n"
if [[ $DRY_RUN == "y" ]]; then
    ssh root@$DOCKER_HOST "cd $PROJECT_PATH && docker compose up -d --force-recreate --remove-orphans --pull always"
    echo -e "${GREEN}Service has been successfully started on the remote host${NC}\n"
    
    ssh root@$DOCKER_HOST "docker image prune -f"
fi
