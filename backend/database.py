from flask_pymongo import PyMongo, wrappers
from pymongo import ASCENDING, GEOSPHERE
import redis, json, random

from model.location import Location
from model.room_info import RoomInfo
from model.security_light import SecurityLight
from model.cctv import CCTV

task_redis = redis.StrictRedis(host='localhost', port=6379, db=2)
search_redis = redis.StrictRedis(host='localhost', port=6379, db=3)
mongo = PyMongo()

def initialize():
    collections = mongo.db.collection_names()
    if "locations" not in collections:
        col: wrappers.Collection = mongo.db.locations
        col.ensure_index([("geo", GEOSPHERE)])

        locations = json.load(open("./db/locations.json"))

        col: wrappers.Collection = mongo.db.locations
        for location in locations:
            loc = Location(**location)
            col.insert_one(loc.__dict__)
        
        subways = json.load(open("./db/subway.json"))
        for subway in subways:
            if not subway:
                continue
            loc = Location(**subway)
            col.insert_one(loc.__dict__)

    if "rooms" not in collections:
        col: wrappers.Collection = mongo.db.rooms
        col.create_index("seq", unique=True)
        col.ensure_index([("geo", GEOSPHERE)])

        col2: wrappers.Collection = mongo.db.room_detail
        col2.create_index("seq", unique=True)
        col2.ensure_index([("geo", GEOSPHERE)])

        db = json.load(open("./db/db.json"))
        for key in db:
            for key2 in db[key]:
                for info in db[key][key2]:
                    try:
                        location = info["locs"][0]["loc"]
                        rooms_info = info["rooms"]

                        col: wrappers.Collection = mongo.db.rooms
                        
                        items = []
                        for rinfo in rooms_info:
                            rinfo["region_code"] = location["code"]
                            room = RoomInfo(**rinfo)
                            items += [ room.__dict__ ]
                        
                        if items:
                            col.insert_many(items)
                    except:
                        pass
                    
                    if not items:
                        continue
                    
                    col: wrappers.Collection = mongo.db.room_detail
                    option = [
                        "침대", "책상", "인터넷", "전자도어락", "세탁기", "에어컨", "옷장", "신발장", "TV", "냉장고", "가스레인지"
                    ]
                    detail = []
                    for item in items:
                        try:
                            item["building_floor"] = random.randint(1, 5)
                            item["floor"] = random.randint(1, item["building_floor"])

                            if item["room_type"] < 3:
                                item["room_count"] = item["room_type"] + 1
                            item["bath_count"] = 1

                            item["reg_date"] = "2020.10.04 22:30"
                            item["building_date"] = "2020.10.04 22:00"

                            item["maintain_cost"] = random.randint(5, 10)
                            cnt = random.randint(0, len(option))
                            item["options"] = random.sample(option, cnt)
                            
                            del item["_id"]
                            col.insert_one(item)
                            detail += [ item ]
                        except:
                            continue
                    #if detail:
                    #    col.insert_many(detail)

    if "security_light" not in collections:
        col: wrappers.Collection = mongo.db.security_light
        col.ensure_index([("geo", GEOSPHERE)])
        db = json.load(open("./db/security_light.json"))
        items = []
        for item in db["records"]:
            if "latitude" in item and "longtitude" in item:
                cctv = SecurityLight(**item)
                items += [ cctv.__dict__ ]

        if items:
            col.insert_many(items)
    
    if "cctv" not in collections:
        col: wrappers.Collection = mongo.db.cctv
        col.ensure_index([("geo", GEOSPHERE)])
        db = json.load(open("./db/cctv.json"))
        items = []
        for item in db["records"]:
            if "latitude" in item and "longtitude" in item:
                cctv = CCTV(**item)
                items += [ cctv.__dict__ ]

        if items:
            col.insert_many(items)
    
    