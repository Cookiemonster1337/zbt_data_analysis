TODO: Implement MongoDB
# import relevant libraries
from pymongo import MongoClient

# initialize mongo connector object with ip adress
client = MongoClient('172.16.134.6')

# get reference to existing database testDB
db = client.testDB

# authentication within database
db.authenticate('mdb_LFD', 'zbtMongo!', source='testDB')

# reference collection, if not existent it will be created
current_collection = db['NMT_TestCollection']

# make sample dict
mydict = {"name": "numbers2",
          "test_array": [1, 3, 4.0, 'test'],
          'second_dict': {'name': 'second_dict',
                          'values': [1, 3, 5, 10, 2.5, 7.0]}}

# insert into database collection
current_collection.insert_one(mydict)

# find entry in collection
entry = current_collection.find_one({'name': 'numbers2'})

# print retrieved entry
print(entry)



