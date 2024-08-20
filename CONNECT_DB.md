# crezazione di utenti e database da utilizzare su MONGODB esistenti

## accesso al server
Se si vuole utilizzare un  database esistente,  anche in replica set,  si deve accedere al server attraverso il terminale.

Se il server utilizza docker per eseguire mongodb,  si deve entrare nel docker container con il comendo 

```bash
docker exec -it mongodb bash
```

## Mongosh

Recuperare la **connection string** ed eseguire il comando di accesso alla `mongosh`.

```bash
mongosh "mongodb://<user>:*******@mongo1.dag.lan:27017,mongo2.dag.lan:27017,mongo3.dag.lan:27017/admin?authSource=admin&replicaSet=rs0"
```

## aggiungere un utente ed un database per il AUTH SERVER

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