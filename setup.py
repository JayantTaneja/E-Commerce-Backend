import pymongo
import json
from credentials import uri



# Connect to MongoDB
client = pymongo.MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("----------------------------")
    print("Connected to Mongodb cluster")
    print("----------------------------")
except Exception as e:
    print(e)

db = client["mydb"]

#---------------------------Loading Dummy Products----------------------------
products_collection = db["products"]

with open("products.json") as f:
    products = json.load(f)

products_collection.create_index("id")

print("Uploading dummy products to cluster")
products_collection.insert_many(products)

client.close()

print("Upload complete")