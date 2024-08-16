# restituisce un dict da poter destrutturare nella creazione di un Pydantic Model
# {"id": "xxxxxx"} ---> **oid(mongo_obj)

oid = lambda x: {"id": str(x["_id"])}
