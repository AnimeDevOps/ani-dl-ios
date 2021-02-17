from databases import Database

try: 
    database = Database("sqlite:///databases/anime_databse.db")
except Exception:
    pass

async def connect():
    await database.connect()
