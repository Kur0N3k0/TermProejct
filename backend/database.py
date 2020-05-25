from flask_pymongo import PyMongo
import redis, json

task_redis = redis.StrictRedis(host='localhost', port=6379, db=2)
mongo = PyMongo()

def initialize():
    collections = mongo.db.collection_names()
    if "rooms" not in collections:
        db = json.load(open("./db.json"))
        for key in db:
            print(key)