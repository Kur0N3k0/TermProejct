from flask_pymongo import PyMongo, wrappers
import redis, json

from model.location import Location
from model.room import Room

task_redis = redis.StrictRedis(host='localhost', port=6379, db=2)
mongo = PyMongo()

def initialize():
    collections = mongo.db.collection_names()
    if "locations" not in collections and "rooms" not in collections:
        col: wrappers.Collection = mongo.db.locations
        col.create_index("id", unique=True)
        col.create_index("code", unique=True)

        col: wrappers.Collection = mongo.db.rooms
        col.create_index("id", unique=True)
        col.create_index("seq", unique=True)

        db = json.load(open("./db.json"))
        for key in db:
            for key2 in db[key]:
                location = None
                for info in db[key][key2]:
                    try:
                        locs = info["locs"][0]["loc"]
                        location = Location(**locs)
                        col: wrappers.Collection = mongo.db.locations
                        col.insert_one(location.__dict__)
                    except Exception as e:
                        pass
                    rooms_info = info["rooms"]

                    col: wrappers.Collection = mongo.db.rooms
                    
                    items = []
                    for rinfo in rooms_info:
                        rinfo["region_code"] = location.code
                        room = Room(**rinfo)
                        items += [ room.__dict__ ]
                    
                    if items:
                        col.insert_many(items)
