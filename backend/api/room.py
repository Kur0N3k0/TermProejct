from flask_pymongo import wrappers
from database import mongo

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
