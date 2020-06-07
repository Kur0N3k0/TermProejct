from flask_pymongo import wrappers
from hashlib import sha256

from database import task_redis, mongo
from model.location import Location
from model.cctv import CCTV
from model.security_light import SecurityLight

class SafetyAPI(object):
    def __init__(self):
        pass

    def getGrade(self, level, cctv, security_light):
        """
        level: kakao map level
        """
        cctv_count = len(cctv)
        sl_count = len(security_light)
        if level == 1:
            
            pass
        elif level == 2:
            pass
        elif level == 3:
            pass
        elif level == 4:
            pass
        elif level == 5:
            pass
        elif level == 6:
            pass
        elif level == 7:
            pass
        else: # error
            return 0xff

    def is_error(self, grade):
        if grade == 0xff:
            return True
        return False

    def getSafetyByRegionCode(self, code):
        col: wrappers.Collection = mongo.db.locations
        location: Location = col.find_one({ "code": code })

        col: wrappers.Collection = mongo.db.cctv
        cctvs = list(col.find({
            "longtitude": {
                "$gte": location.bbox[0][0],
                "$lte": location.bbox[1][0]
            },
            "latitude": {
                "$gte": location.bbox[0][1],
                "$lte": location.bbox[1][1]
            }
        }))

        col: wrappers.Collection = mongo.db.security_light
        security_lights = list(col.find({
            "longtitude": {
                "$gte": location.bbox[0][0],
                "$lte": location.bbox[1][0]
            },
            "latitude": {
                "$gte": location.bbox[0][1],
                "$lte": location.bbox[1][1]
            }
        }))

        return self.getGrade(7, cctvs, security_lights)
    