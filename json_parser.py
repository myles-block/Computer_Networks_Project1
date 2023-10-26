import pymongo
import json
from pymongo_get_database import get_database

INPUT_FILE = "smaller_json.json"

def json_parser():
    with open(INPUT_FILE, 'r') as file:
        data = json.load(file)
    dbname = get_database()
    collection_name = dbname["myles_ipRange1"]
    print("inserting")
    collection_name.insert_many(data)

json_parser()