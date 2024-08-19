admin = db.getSiblingDB("admin")

admin.createUser({
    user: process.env.MONGO_USER,
    pwd: "xxx",
    roles: [
        { db: process.env.MONGO_DB, role: "readWrite" },
        { db: process.env.MONGO_DB, role: "dbOwner" },
    ]
})


// db.changeUserPassword("myusername", passwordPrompt())
// mydb = db.getSiblingDB('mydb')
// coll1 = users.createCollection("mycollection1")
// coll2 = users.createCollection("mycollection2")
