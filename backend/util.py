import string, random
from functools import wraps
from flask import session, redirect, request, jsonify
from flask_pymongo import pymongo, wrappers

from database import mongo
# from models.token import Token
from model.user import User

def login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if session.get("userinfo") == None:
            return redirect("/proto/signin")
        return func(*args, **kwargs)
    return deco

def admin_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        info = session.get("userinfo")
        if info == None:
            return redirect("/proto/signin")
        if info["level"] != User.ADMIN:
            return redirect("/")
        return func(*args, **kwargs)
    return deco

def roomuser_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if session.get("userinfo") == None:
            return redirect("/proto/signin/roomuser")
        level = session["userinfo"]["level"]
        if level != User.ADMIN and level != User.ROOM_USER:
            return jsonify({ "result": "Authority error" })
        return func(*args, **kwargs)
    return deco

# def xtoken_required(func):
#     @wraps(func)
#     def deco(*args, **kwargs):
#         token = request.headers.get("X-Access-Token")
#         if not token or not xtoken_valid(token):
#             return redirect("/api/v1/error")
#         return func(*args, **kwargs)
#     return deco

# def xtoken_valid(xtoken):
#     token_db: wrappers.Collection = mongo.db.token
#     token: Token = deserialize_json(Token, token_db.find_one({ "token": xtoken }))
#     if not token:
#         return False
    
#     if token.expire_date >= time.time():
#         return False

#     return True

# def xtoken_user(xtoken):
#     token_db: wrappers.Collection = mongo.db.token
#     token: Token = deserialize_json(Token, token_db.find_one({ "token": xtoken }))
#     db: wrappers.Collection = mongo.db.users
#     return deserialize_json(User, db.find_one({ "uuid": token.tenant }))

def randomString(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def deserialize_json(cls=None, data=None):
    if data == None:
        return None
        
    if isinstance(data, list):
        r = []
        for item in data:
            instance = object.__new__(cls)
            for key, value in item.items():
                if key == "_id":
                    continue
                setattr(instance, key, value)
            r += [instance]
        return r
    elif isinstance(data, pymongo.cursor.Cursor):
        cursor: pymongo.cursor.Cursor = data
        r = []
        for item in cursor:
            instance = object.__new__(cls)
            for key, value in item.items():
                if key == "_id":
                    continue
                setattr(instance, key, value)
            r += [instance]
        return r
    else:
        instance = object.__new__(cls)
        for key, value in data.items():
            if key == "_id":
                continue
            setattr(instance, key, value)

        return instance