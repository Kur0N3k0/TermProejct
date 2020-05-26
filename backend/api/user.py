from flask_pymongo import wrappers
from hashlib import sha256

from database import task_redis, mongo
from model.user import User
from model.room_user import RoomUser

class UserAPI(object):
    def __init__(self):
        col: wrappers.Collection = mongo.db.users
        indexes = col.list_indexes()
        if "username" not in indexes:
            col.create_index("username", unique=True)
        
        col: wrappers.Collection = mongo.db.roomusers
        indexes = col.list_indexes()
        if "username" not in indexes:
            col.create_index("username", unique=True)
        if "email" not in indexes:
            col.create_index("email", unique=True)
        if "phone" not in indexes:
            col.create_index("phone", unique=True)

    def signup(self, username, password):
        col: wrappers.Collection = mongo.db.users
        try:
            user = User(username, sha256(password).hexdigest().decode())
            col.insert_one(user.__dict__)
        except:
            return False
        return True
    
    def signup_roomuser(self, username, password, name, email, phone):
        # TODO: email verify
        col: wrappers.Collection = mongo.db.roomusers
        try:
            user = RoomUser(
                username,
                sha256(password).hexdigest().decode(),
                name, email, phone
            )
            col.insert_one(user.__dict__)
        except:
            return False
        return True
    
    def signin(self, username, password):
        col: wrappers.Collection = mongo.db.users
        result = col.find_one({
            "username": username,
            "password": sha256(password).hexdigest().decode()
        })
        if not result:
            return False
        return result
    
    def signin_roomuser(self, username, password):
        col: wrappers.Collection = mongo.db.roomusers
        result = col.find_one({
            "username": username,
            "password": sha256(password).hexdigest().decode()
        })
        if not result:
            return False
        return result