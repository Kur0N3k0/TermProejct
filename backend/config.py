import json

class Config(object):
    @staticmethod
    def get(key):
        return json.load(open("./config.js"))[key]
    