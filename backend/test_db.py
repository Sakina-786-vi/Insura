from surrealdb import Surreal

db = Surreal("ws://127.0.0.1:8000")

db.signin({
    "username": "root",
    "password": "root"
})

db.use("insura", "main")

print("Connected to SurrealDB!")

db.close()