import pymongo
from sqlalchemy import create_engine

try:
    # Test Mongo
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    print("✅ MongoDB is UP and running in Docker!")

    # Test Postgres
    engine = create_engine("postgresql://postgres:123456@localhost:5432/reddit_db")
    connection = engine.connect()
    print("✅ Postgres is UP and running in Docker!")
    connection.close()

except Exception as e:
    print(f"❌ Connection Failed: {e}")