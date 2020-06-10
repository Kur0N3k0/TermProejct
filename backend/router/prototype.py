from flask import Flask, url_for, request, session, render_template, redirect, Blueprint, jsonify
from flask_pymongo import wrappers

from database import task_redis, search_redis, mongo
from api.user import UserAPI
from api.room import RoomAPI
from api.location import LocationAPI
from api.cctv import CCTVAPI
from api.security_light import securityLightAPI
from api.building import BuildingAPI
from model.location import Location

import uuid, json, hashlib
import pymongo
import tasks

router = Blueprint("proto", __name__)
userapi = UserAPI()
roomAPI = RoomAPI()
locationAPI = LocationAPI()
cctvAPI = CCTVAPI()
seclightAPI = securityLightAPI()
buildingAPI = BuildingAPI()

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

    return jsonify(result[:20])

@router.route("/room")
def searchRoom():
    full_name = request.args.get("full_name", "")
    longtitude = float(request.args.get("longtitude", 126.570667))
    latitude = float(request.args.get("latitude", 33.450701))
    room_range = int(request.args.get("room_range", 1000))

    return render_template("/prototype.html", keyword={
        "full_name": full_name,
        "longtitude": longtitude,
        "latitude": latitude,
        "room_range": room_range,
    })

@router.route("/rooms")
def searchRooms():
    longtitude = float(request.args.get("longtitude", 126.570667))
    latitude = float(request.args.get("latitude", 33.450701))
    room_range = int(request.args.get("room_range", 1000))
    rtype = request.args.get("room_type", "")

    key = str(longtitude) + str(latitude) + str(room_range) + rtype
    cache_key = hashlib.sha1(key.encode()).hexdigest()

    result = search_redis.get(cache_key)
    if result:
        return jsonify(json.loads(result))

    if rtype:
        cond = { "room_type_str": rtype }
        rooms = roomAPI.getRoomsByCoordAndCond(cond, longtitude, latitude, room_range)
    else:
        rooms = roomAPI.getRoomsByCoord(longtitude, latitude, room_range)

    for room in rooms:
        del room["_id"]

    # get region info
    if not rooms:
        result = {
            "rooms": [],
            "longtitude": longtitude,
            "latitude": latitude,
            "security_light": [],
            "cctv": [],
        }
        return result

    longtitude = rooms[0]["random_location"][0]
    latitude = rooms[0]["random_location"][1]

    # filter check
    CCTV, SECLIGHT, SUBWAY, BUILDING = 0, 1, 2, 3
    search_filter = [ False for _ in range(4) ]
    if request.args.get("cctv", None):
        search_filter[CCTV] = True
    if request.args.get("seclight", None):
        search_filter[SECLIGHT] = True
    if request.args.get("subway", None):
        search_filter[SUBWAY] = True
    if request.args.get("building", None):
        search_filter[BUILDING] = True

    seclight_range = int(request.args.get("seclight_range", 300))
    cctv_range = int(request.args.get("cctv_range", 300))
    subway_range = int(request.args.get("subway_range", 300))
    building_range = int(request.args.get("building_range", 300)) / 1000
    bfilter = request.args.get("bfilter", "")
    bfilter = bfilter.split(",")

    # filter
    if search_filter.count(True):
        for room in rooms:
            count = 0
            if search_filter[SECLIGHT]:
                count += len(seclightAPI.getLightByLocation(room.random_location[0], room.random_location[1], seclight_range))
            if search_filter[CCTV]:
                count += len(cctvAPI.getCCTVByLocation(room.random_location[0], room.random_location[1], cctv_range))
            if search_filter[SUBWAY]:
                count += len(locationAPI.getLocationsByCoord("subway", room.random_location[0], room.random_location[1], subway_range))
            if search_filter[BUILDING]:
                count += len(buildingAPI.getBuildings(longtitude, latitude, building_range, 100, bfilter))
            room["counting"] = count
        return jsonify({ "rooms": rooms })

    # get security_light info
    # security_light address: mixed data(new, old...)
    security_lights = seclightAPI.getLightByLocation(longtitude, latitude, seclight_range)
    for security_light in security_lights:
        del security_light["_id"]

    # get cctv info
    # cctv address: mixed data(new, old...)
    cctvs = cctvAPI.getCCTVByLocation(longtitude, latitude, cctv_range)
    for cctv in cctvs:
        del cctv["_id"]

    # get subway info
    subways = locationAPI.getLocationsByCoord("subway", longtitude, latitude, subway_range)
    for subway in subways:
        del subway["_id"]

    result = {
        "rooms": rooms,
        "longtitude": longtitude,
        "latitude": latitude,
        "security_light": security_lights,
        "cctv": cctvs,
    }

    value = json.dumps(result)
    search_redis.set(cache_key, value, ex=3600 * 24)

    return jsonify(result)

@router.route("/room/pick/<roomid>")
def roomPick(roomid):
    col: wrappers.Collection = mongo.db.rooms
    query = {}
    query["id"] = roomid
    result = col.find_one(col)
    del result["_id"]
    return jsonify(result)

@router.route("/building")
def building():
    longtitude = float(request.args.get("longtitude", 0.0))
    latitude = float(request.args.get("latitude", 0.0))

    # default range: 10km
    bfilter = request.args.get("bfilter", "")
    bfilter = bfilter.split(",")

    building = buildingAPI.getBuildings(longtitude, latitude, 10.0, 100, bfilter)
    return jsonify(building)

@router.route("/building/detail/<pnu>")
def building_detail(pnu):
    detail = buildingAPI.getDetail(pnu)
    return jsonify(detail)

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