from flask import session
from flask_pymongo import wrappers
from datetime import datetime

from database import mongo
from model.room_info import RoomInfo
from util import deserialize_json, randomString
from hashlib import md5

class Room(RoomInfo):
    def __init__(self, **kwargs):
        if kwargs:
            RoomInfo.__init__(self, kwargs)
            self.floor = int(kwargs["floor"])
            self.building_floor = int(kwargs["building_floor"])
            self.room_count = int(kwargs["room_count"])
            self.bath_count = int(kwargs["bath_count"])
            self.reg_date = kwargs["reg_date"]
            self.building_date = kwargs["building_date"]
            self.maintain_cost = int(kwargs["maintain_cost"])
            self.options = kwargs["options"]

    def to_parent(self):
        return RoomInfo(**self.__dict__)

    @staticmethod
    def getRoomTypeStr(room_type):
        if room_type == 0:
            return "원룸"
        elif room_type == 1:
            return "투룸"
        elif room_type == 2:
            return "쓰리룸"
        return "원룸"

    @staticmethod
    def from_request(form, is_update=False):
        col: wrappers.Collection = mongo.db.room_detail
        info = deserialize_json(RoomInfo, col.find().sort("seq", -1).limit(1))

        room = Room()
        room.is_favorited           = False
        room.seq                    = info[0].seq + 1
        if is_update:
            room.seq                = int(form["seq"])
        room.id                     = md5(randomString(10).encode()).hexdigest()
        room.user_id                = session["userinfo"]["username"]
        room.deleted                = False
        room.name                   = session["userinfo"]["name"]
        room.title                  = form["title"]
        room.room_type              = int(form["room_type"])
        room.random_location        = form.getlist("random_location[]", float)
        room.geo                    = {
            "type": "Point",
            "coordinates": room.random_location
        }
        room.complex_name           = None
        room.premium_badge          = False
        room.hash_tags              = form.getlist("hash_tags[]")
        room.room_type_str          = Room.getRoomTypeStr(room.room_type)
        room.room_desc              = form["room_desc"]
        room.img_url                = form["img_url"]
        room.img_urls               = form.getlist("img_urls[]")
        room.is_pano                = False
        room.price_title            = form["price_title"]
        room.selling_type           = 0
        room.is_confirm             = False
        room.confirm_type           = None
        room.confirm_date_str       = ""
        room.is_quick               = False
        room.is_messenger_actived   = True
        
        # related with location.code
        room.region_code            = form["region_code"]

        room.floor                  = int(form["floor"])
        room.building_floor         = int(form["building_floor"])
        room.room_count             = int(form["room_type"]) + 1
        room.bath_count             = 1
        room.reg_date               = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # today
        room.building_date          = form["building_date"]
        room.maintain_cost          = int(form["maintain_cost"])
        room.options                = form.getlist("options[]")

        return room
