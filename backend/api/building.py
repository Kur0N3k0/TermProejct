from pyproj import Proj, transform
from api.geo import Geo
from config import Config
import requests
import xml.etree.ElementTree as ET

# korea coordinate system
UTMK = Proj(init='epsg:5174')

# longtitude, latitude
WGS84 = Proj(init='epsg:4326')

class Building(object):
    def __init__(self):
        self.external_api = "http://apis.data.go.kr/1611000/nsdi/BuildingUseService"
        self.sess = requests.Session()

    def __requestWFS(self, srsName, circle_range, count):
        param = {
            "ServiceKey": Config.get("WFSkey"),
            "bbox": "",
            "maxFeatures": str(count),
            "srsName": "EPSG:4326",
            "resultType": "results"
        }
        result = self.sess.get(self.external_api, param=param).text
        root = ET.fromstring(result)
        return root

    def getBuildings(self, coordinate):
        pass
        