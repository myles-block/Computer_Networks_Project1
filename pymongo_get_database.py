from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb+srv://myles_block11:Danial03_Adin19@networkdb.mzzzkl8.mongodb.net/?retryWrites=true&w=majority"
 
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(CONNECTION_STRING)

   try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
   except Exception as e:
    print(e)

   # Create the database for our example (we will use the same database throughout the tutorial
   return client['ip_lists'] # this is the name of the database
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = get_database()