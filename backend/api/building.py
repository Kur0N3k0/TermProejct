from pyproj import Proj, transform
from api.geo import Geo
from config import Config
import requests
import xml.etree.ElementTree as ET

# korea coordinate system
UTMK = Proj(init='epsg:5174')

# longtitude, latitude
WGS84 = Proj(init='epsg:4326')

class BuildingAPI(object):
    def __init__(self):
        self.external_api = {
            "WFS": "http://apis.data.go.kr/1611000/nsdi/BuildingUseService/wfs/getBuildingUseWFS",
            "Prop": "http://apis.data.go.kr/1611000/nsdi/BuildingUseService/attr/getBuildingUse"
        }
        self.filter = Config.get("Building")["filter"]
        self.sess = requests.Session()

    def __requestWFS(self, longtitude, latitude, km: float, count, bfilter=None):
        low_lat, low_lon, hi_lat, hi_lon = Geo.boundingBox(latitude, longtitude, km)
        low_coord = Geo.transformCoordinate(WGS84, UTMK, (low_lon, low_lat))
        hi_coord = Geo.transformCoordinate(WGS84, UTMK, (hi_lon, hi_lat))
        
        bbox = ",".join(map(str, [*low_coord, *hi_coord])) + ",EPSG:5174"

        param = {
            "ServiceKey": Config.get("WFSkey"),
            "bbox": bbox,
            "maxFeatures": str(count),
            "srsName": "EPSG:5174",
            "resultType": "results"
        }
        result = self.sess.get(self.external_api["WFS"], params=param).text
        root = ET.fromstring(result)
        gml = "{http://www.opengis.net/gml}"
        nsdl = "{http://openapi.nsdi.go.kr}"

        r = []
        result = root.iter(f"{gml}featureMember")
        for item in result:
            pos = next(item.iter(f"{gml}posList")).text
            pnu = next(item.iter(f"{nsdl}PNU")).text
            main_code = next(item.iter(f"{nsdl}MAIN_PRPOS_CODE")).text
            main_name = next(item.iter(f"{nsdl}MAIN_PRPOS_CODE_NM")).text
            detail_code = next(item.iter(f"{nsdl}DETAIL_PRPOS_CODE")).text
            detail_name = next(item.iter(f"{nsdl}DETAIL_PRPOS_CODE_NM")).text

            # use default filter
            if not bfilter:
                if detail_code not in self.filter:
                    continue
            else:
                if detail_code not in bfilter:
                    continue

            polyLine = []
            pos = pos.split(" ")
            for i in range(0, len(pos), 2):
                polyLine += [ Geo.transformCoordinate(UTMK, WGS84, (pos[i], pos[i + 1])) ]

            p = {
                "polyLine": polyLine,
                "pnu": pnu,
                "maincode": main_code,
                "mainname": main_name,
                "detailcode": detail_code,
                "detailname": detail_name
            }
            r += [ p ]

        return r
    
    def __requestDetail(self, pnu):
        param = {
            "ServiceKey": Config.get("WFSkey"),
            "pageNo": "1",
            "numOfRows": "10",
            "pnu": pnu,
            "format": "json"
        }
        result = self.sess.get(self.external_api["Prop"], params=param).json()
        field = result["buildingUses"]["field"]
        return field

    def getBuildings(self, longtitude, latitude, km:float, count, bfilter):
        return self.__requestWFS(longtitude, latitude, km, count, bfilter)
    
    def getDetail(self, pnu):
        return self.__requestDetail(pnu)