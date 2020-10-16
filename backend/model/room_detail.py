from flask import session
from flask_pymongo import wrappers

from database import mongo
from model.room_info import RoomInfo
from util import deserialize_json, randomString
from hashlib import md5

class Room(RoomInfo):
    def __init__(self, **kwargs):
        if kwargs:
            super(self, kwargs)
            self.floor = int(kwargs["floor"])
            self.building_floor = int(kwargs["building_floor"])
            self.room_count = int(kwargs["room_count"])
            self.bath_count = int(kwargs["bath_count"])
            self.reg_date = kwargs["reg_date"]
            self.building_date = kwargs["building_date"]
            self.maintain_cost = int(kwargs["maintain_cost"])
            self.options = kwargs["options"]

    @staticmethod
    def from_request(form, is_update=False):
        col: wrappers.Collection = mongo.db.rooms
        info = deserialize_json(RoomInfo, col.find(query).sort({ "seq": -1 }).limit(1))

        room = Room()
        room.is_favorited           = form["is_favorited"]
        room.seq                    = info.seq + 1
        if is_update:
            room.seq                = int(form["seq"])
        room.id                     = md5(randomString(10)).hexdigest()
        room.user_id                = session["userinfo"]["username"]
        room.deleted                = False
        room.name                   = session["userinfo"]["name"]
        room.title                  = form["title"]
        room.room_type              = form["room_type"]
        room.random_location        = form["random_location"]
        room.geo                    = {
            "type": "Point",
            "coordinates": [ room.random_location[0], room.random_location[1] ]
        }
        room.complex_name           = form["complex_name"]
        room.premium_badge          = False
        room.hash_tags              = form["hash_tags"]
        room.room_type_str          = form["room_type_str"]
        room.room_desc              = form["room_desc"]
        room.img_url                = form["img_url"]
        room.img_urls               = form["img_urls"]
        room.is_pano                = form["is_pano"]
        room.price_title            = form["price_title"]
        room.selling_type           = form["selling_type"]
        room.is_confirm             = form["is_confirm"]
        room.confirm_type           = form["confirm_type"]
        room.confirm_date_str       = form["confirm_date_str"]
        room.is_quick               = form["is_quick"]
        room.is_messenger_actived   = form["is_messenger_actived"]
        
        # related with location.code
        room.region_code            = form["region_code"]

        room.floor                  = int(form["floor"])
        room.building_floor         = int(form["building_floor"])
        room.room_count             = int(form["room_count"])
        room.bath_count             = int(form["bath_count"])
        room.reg_date               = form["reg_date"]
        room.building_date          = form["building_date"]
        room.maintain_cost          = int(form["maintain_cost"])
        room.options                = form["options"]

        return room