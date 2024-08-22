# Creazione di utenti e database da utilizzare su MONGODB esistenti

Si  esegua lo script che genera in automatico le credenziali per il nuovo utente, così come i comandi per ACCEDERE e MODIFICARE il database.

```bash
bash ./lib/scripts/0.generate-credentials.zsh
```

## Accesso al server
Se si vuole utilizzare un  database esistente,  anche in replica set,  si deve accedere al server attraverso il terminale.

Le credenziali generate con lo script precedente offrono diversi tipi di accesso e relativi snippet di comandi da utilizzare. Le modalità sono due: 

### **from_host** dall'host che esegue il docker engine

```bash
docker exec -it mongodb mongosh "<connection string>"

# oppure 

docker exec -it mongodb mongosh -u <user> -p $(cat /var/mongo/MONGO_ROOT_PW)
```

### **from_container** allínterno del container che esegue mongodb.

Se il server utilizza docker per eseguire mongodb,  si deve entrare nel docker container con il comando 

```bash
#  from host
docker exec -it mongodb bash
```

```bash
#  from container 

mongosh "<connection string>"

# oppure

mongosh -u <user> -p $(cat /run/secrets/MONGO_ROOT_PW) --authenticationDatabase admin
```


## Aggiungere un utente ed un database per il AUTH SERVER

Sempre nello script sono indicati i comandi da lanciare nella **mongosh** per aggiungere e modificare l'utente.

Nell'ambiente mongosh aggiungere un utente ed un database che veranno utilizzati per scrivere le info del AUTH-SERVER

```javascript
admin = db.getSiblingDB("admin")

admin.createUser({
    user: "auth_user",
    pwd: "************************",
    roles: [
        { db: "auth", role: "readWrite" },
        { db: "auth", role: "dbOwner" },
    ]
})
```
# Creazione di un database dedicato a utilizzare un un progetto *compose*

vedi la configurazione di docker-compose.dev.yaml