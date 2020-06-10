from flask_pymongo import wrappers
from database import mongo

class LocationAPI(object):
    def __init__(self):
        pass

    def getLocationsByCoord(self, ltype, longtitude, latitude, circle_range):
        col: wrappers.Collection = mongo.db.locations

        result = list(col.find({
            "type": ltype,
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