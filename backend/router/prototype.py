from flask import Flask, url_for, request, session, render_template, redirect, Blueprint, jsonify
from flask_pymongo import wrappers
from werkzeug.utils import secure_filename

from database import task_redis, search_redis, mongo
from api.user import UserAPI
from api.room import RoomAPI
from api.location import LocationAPI
from api.cctv import CCTVAPI
from api.security_light import securityLightAPI
from api.building import BuildingAPI
from model.location import Location
from model.room_detail import Room
from model.user import User
from util import login_required, roomuser_required
from config import Config
from appctx import app

import uuid, json, hashlib, os, time
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
    return render_template("prototype.html", keyword={
        "full_name": "",
        "longtitude": 126.570667,
        "latitude": 33.450701,
        "room_range": 1000,
    })

################################################
# user
################################################
@router.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        user = userapi.signin(username, password)
        if not user:
            return jsonify({"error": 1})
        session["userinfo"] = user
        return jsonify({})
    return render_template("signin.html")

@router.route("/signin/roomuser", methods=["GET", "POST"])
def signin_roomuser():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        user = userapi.signin_roomuser(username, password)
        if not user:
            return jsonify({"error": 1})
        session["userinfo"] = user
        return jsonify({})
    return render_template("ru_signin.html")
    
@router.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@router.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        if not userapi.signup(username, password):
            return jsonify({"error": 1})
        return jsonify({})
    return render_template("signup.html")

@router.route("/signup/roomuser", methods=["GET", "POST"])
def signup_roomuser():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        if not userapi.signup_roomuser(username, password, name, email, phone):
            return jsonify({"error": 1})
        return jsonify({})
    return render_template("ru_signup.html")

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

    return render_template("/prototype.html", keyword={
        "full_name": full_name,
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

    seclight_range = int(request.args.get("seclight_range", 300))
    cctv_range = int(request.args.get("cctv_range", 300))
    subway_range = int(request.args.get("subway_range", 300))
    building_range = int(request.args.get("building_range", 300)) / 1000

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

@router.route("/rooms/filter")
def roomsFilter():
    room_ids = request.args.get("rooms", None)
    if not room_ids:
        return jsonify({ "rooms": [] })
    
    room_ids = list(map(int, set(room_ids.split(","))))
    rooms = roomAPI.getRoomsBySeqs(room_ids)
    for room in rooms:
        del room["_id"]

    # filter check
    CCTV, SECLIGHT, SUBWAY, BUILDING = 0, 1, 2, 3
    search_filter = [ False for _ in range(4) ]
    if request.args.get("cctv", None) != None:
        search_filter[CCTV] = True
    if request.args.get("seclight", None) != None:
        search_filter[SECLIGHT] = True
    if request.args.get("subway", None) != None:
        search_filter[SUBWAY] = True
    if request.args.get("building", None) != None:
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
            room["count"] = {
                "seclight": 0,
                "cctv": 0,
                "subway": 0,
                "building": 0
            }
            if search_filter[SECLIGHT]:
                room["count"]["seclight"] = len(seclightAPI.getLightByLocation(room["random_location"][0], room["random_location"][1], seclight_range))
            if search_filter[CCTV]:
                room["count"]["cctv"] = len(cctvAPI.getCCTVByLocation(room["random_location"][0], room["random_location"][1], cctv_range))
            if search_filter[SUBWAY]:
                room["count"]["subway"] = len(locationAPI.getLocationsByCoord("subway", room["random_location"][0], room["random_location"][1], subway_range))
            if search_filter[BUILDING]:
                room["count"]["building"] = len(buildingAPI.getBuildings(room["random_location"][0], room["random_location"][1], building_range, 100, bfilter))
        return jsonify({ "rooms": rooms })

    return jsonify({ "rooms": [] })

@router.route("/room/create", methods=["GET", "POST"])
def roomCreate():
    if request.method == "POST":
        room = Room.from_request(request.form)
        roomAPI.createRoom(room)
        return jsonify({ "status": True })
    
    return render_template("/roomcreate.html")

@router.route("/room/list")
@roomuser_required
def roomList():
    user_id = session["userinfo"]["username"]
    if not user_id:
        return jsonify({ "status": -3 })
    
    result = roomAPI.listRoom(user_id)
    return render_template("/roomlist.html", rooms=result)

@router.route("/room/<int:seq>")
@roomuser_required
def roomDetail(seq):
    result = roomAPI.getRoomDetail(seq)
    if not result:
        result = None
    return render_template("/roomdetail.html", room=result)

@router.route("/room/update/<int:seq>")
@roomuser_required
def roomUpdate(seq):
    if request.method == "POST":
        room = Room.from_request(request.form, is_update=True)
        roomAPI.updateRoom(seq, room)
        return jsonify({ "status": True })

    room = roomAPI.getRoomDetail(seq)
    return render_template("roomupdate.html", seq=seq, room=room)

@router.route("/room/delete", methods=["POST"])
@roomuser_required
def roomDeleteMany():
    seqs = request.form.getlist("seqs[]", int)
    roomAPI.deleteRoomMany(seqs)
    return jsonify({ "status": True })

@router.route("/room/delete/<int:seq>")
@roomuser_required
def roomDelete(seq):
    roomAPI.deleteRoom(seq)
    return jsonify({ "status": True })

@router.route("/room/upload", methods=["POST"])
@roomuser_required
def roomUpload():
    images = request.files.getlist("images[]")
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    result = []
    for image in images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            filename = hashlib.sha256(str(time.time()).encode() + filename.encode() + b"_saltbae_").hexdigest() + "." + ext
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            result += [ filename ]

    return jsonify({ "result": result })

@router.route("/room/image/delete/<path>")
@roomuser_required
def roomImageDelete(path):
    os.unlink(os.path.join(app.config["UPLOAD_FOLDER"], path))
    return "deleted"

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

@router.route("/building/getfilter")
def building_config():
    return jsonify(Config.get("Building")["filter"])

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