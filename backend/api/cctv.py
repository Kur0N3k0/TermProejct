from flask_pymongo import wrappers
from database import mongo
from math import *

class CCTVAPI(object):
    def __init__(self):
        pass

    def getCCTVByLocation(self, longtitude, latitude, circle_range):
        col: wrappers.Collection = mongo.db.cctv

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
