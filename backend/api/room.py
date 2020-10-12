from flask_pymongo import wrappers
from database import mongo
from model.room_detail import Room
from util import deserialize_json

class RoomAPI(object):
    def __init__(self):
        pass

    def getRoomsByCoord(self, longtitude, latitude, circle_range):
        col: wrappers.Collection = mongo.db.rooms

        result = list(col.find({
            "geo": {
                "$near": {
                    "$maxDistance": circle_range,
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [ longtitude, latitude ]
                    }
                }
            }
        }))

        return result

    def getRoomsByCoordAndCond(self, cond, longtitude, latitude, circle_range):
        col: wrappers.Collection = mongo.db.rooms

        query = {
            "geo": {
                "$near": {
                    "$maxDistance": circle_range,
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [ longtitude, latitude ]
                    }
                }
            }
        }
        query.update(cond)

        result = list(col.find(query))

        return result

    def getRoomsBySeqs(self, seqs):
        col: wrappers.Collection = mongo.db.rooms

        query = {
            "seq": {
                "$in": seqs
            }
        }
        return list(col.find(query))
    
    def getRoomDetail(self, seq):
        col: wrappers.Collection = mongo.db.room_detail
        return deserialize_json(Room, col.find_one({ "seq": seq }))

    def createRoom(self, detail: Room):
        col: wrappers.Collection = mongo.db.room_detail
        col.insert_one(detail.to_dict())
    
    def listRoom(self, user_id):
        col: wrappers.Collection = mongo.db.room_detail
        return list(col.find({ "user_id": user_id }))

    def updateRoom(self, seq, detail: Room):
        col: wrappers.Collection = mongo.db.room_detail
        col.update_one({ "seq": seq }, detail.to_dict())
    
    def deleteRoom(self, seq):
        col: wrappers.Collection = mongo.db.room_detail
        col.delete_one({ "seq": seq })