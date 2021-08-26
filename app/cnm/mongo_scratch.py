import pymongo

import config


client = pymongo.MongoClient(config.MONGO_URI)
db = client.get_database("casper")
print(db.name)
