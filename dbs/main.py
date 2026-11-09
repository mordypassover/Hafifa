import dotenv
from pymongo import MongoClient
import os

dotenv.load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]

client = MongoClient(MONGO_URI)

db = client["test_db"]
collection = db["users"]



print("Total documents:", collection.count_documents({}))

for doc in collection.find():
    print(doc)

print(collection.find({}))


client.close()
