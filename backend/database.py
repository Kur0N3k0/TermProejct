from flask_pymongo import PyMongo
import redis

task_redis = redis.StrictRedis(host='localhost', port=6379, db=2)
mongo = PyMongo()