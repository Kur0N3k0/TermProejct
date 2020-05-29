from flask import Flask, url_for, request, session, render_template, redirect, Blueprint, jsonify
from flask_pymongo import wrappers

from database import task_redis, mongo
from api.user import UserAPI
from model.location import Location

import uuid, json
import pymongo
import tasks

router = Blueprint("proto", __name__)
userapi = UserAPI()

@router.route("/")
def main():
    return render_template("prototype.html")

################################################
# user
################################################
@router.route("/signin")
def signin():
    username, password = request.form["username"], request.form["password"]
    user = userapi.signin(username, password)
    if not user:
        return "user not found"
    session["userinfo"] = user
    return "signin"

@router.route("/signin/roomuser")
def signin_roomuser():
    username, password = request.form["username"], request.form["password"]
    user = userapi.signin_roomuser(username, password)
    if not user:
        return "user not found"
    session["userinfo"] = user
    return "signin"
    
@router.route("/logout")
def logout():
    session.clear()
    return "bye"

@router.route("/signup")
def signup():
    username, password = request.form["username"], request.form["password"]
    if not userapi.signup(username, password):
        return "signup failed"
    return "signup"

@router.route("/signup/roomuser")
def signup_roomuser():
    username, password = request.form["username"], request.form["password"]
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    if not userapi.signup_roomuser(username, password, name, email, phone):
        return "signup failed"
    return "signup"

################################################
# search location & room
################################################
@router.route("/search")
def searchLocations():
    query = {}
    col: wrappers.Collection = mongo.db.locations

    region = request.args.get("region")
    if region:
        query["full_name"] = { "$regex": region }

    subway = request.args.get("subway")
    if subway:
        query["subways"] = { "$regex": subway }

    result = list(col.find(query).sort([("full_name", pymongo.ASCENDING)]))
    for item in result:
        del item["_id"]

    return jsonify(result)

@router.route("/rooms/<region>")
def searchRooms(region):
    query = {}
    col: wrappers.Collection = mongo.db.rooms

    if region:
        query["region_code"] = region

    # get rooms in region
    rooms = list(col.find(query))
    for item in rooms:
        del item["_id"]

    # get region info
    col: wrappers.Collection = mongo.db.locations
    loc = col.find_one({ "code": region })
    del loc["_id"]
    location = Location(**loc)

    # get cctv info
    # cctv address: mixed data(new, old...)
    col: wrappers.Collection = mongo.db.cctv
    cctvs = list(col.find({
        "longtitude": {
            "$gte": location.bbox[0][0],
            "$lte": location.bbox[1][0]
        },
        "latitude": {
            "$gte": location.bbox[0][1],
            "$lte": location.bbox[1][1]
        }
    }))
    for cctv in cctvs:
        del cctv["_id"]

    result = {
        "rooms": rooms,
        "location": location.__dict__,
        "cctv": cctvs
    }

    return jsonify(result)

@router.route("/room/pick/<roomid>")
def roomPick(roomid):
    col: wrappers.Collection = mongo.db.rooms
    query = {}
    query["id"] = roomid
    result = col.find_one(col)
    del result["_id"]
    return jsonify(result)


################################################
# Celery front task...
# information lifecycle
# expire: 1 day
################################################
@router.route("/region/safety/<region>")
def regionSafety(region):
    cached = task_redis.get(region)
    if not cached:
        task = tasks.getRegionSafety.apply_async(args=(region,))

        info = json.dumps({
            "taskid": task.id,
            "result": ""
        })

        task_redis.set(region, info, ex=3600 * 24) # 1 day
        return f"task accepted({task.id})"

    cached = json.loads(cached)
    taskid = cached["taskid"]
    task = tasks.getRegionSafety.AsyncResult(taskid)
    if task.state == "PROGRESS":
        return task.info
    elif task.state != "FAILURE":
        cached["result"] = task.info
        cached = json.dumps(cached)
        task_redis.set(region, cached, ex=3600 * 24)
        return cached

    return cached