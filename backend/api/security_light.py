from flask_pymongo import wrappers
from database import mongo

class securityLightAPI(object):
    def __init__(self):
        pass

    def getLightByLocation(self, longtitude, latitude, circle_range):
        col: wrappers.Collection = mongo.db.security_light

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
