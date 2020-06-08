from pyproj import Proj, transform

import numbers
import math

class Geo:
    """
    Geographical Utils
    """
    @staticmethod
    def degree2radius(degree):
        return degree * (math.pi/180)
    
    @staticmethod
    def get_harversion_distance(x1, y1, x2, y2, round_decimal_digits=5):
        """
        경위도 (x1,y1)과 (x2,y2) 점의 거리를 반환
        Harversion Formula 이용하여 2개의 경위도간 거래를 구함(단위:Km)
        """
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        assert isinstance(x1, numbers.Number) and -180 <= x1 and x1 <= 180
        assert isinstance(y1, numbers.Number) and  -90 <= y1 and y1 <=  90
        assert isinstance(x2, numbers.Number) and -180 <= x2 and x2 <= 180
        assert isinstance(y2, numbers.Number) and  -90 <= y2 and y2 <=  90

        R = 6371 # 지구의 반경(단위: km)
        dLon = Geo.degree2radius(x2-x1)    
        dLat = Geo.degree2radius(y2-y1)

        a = math.sin(dLat/2) * math.sin(dLat/2) \
            + (math.cos(Geo.degree2radius(y1)) \
              *math.cos(Geo.degree2radius(y2)) \
              *math.sin(dLon/2) * math.sin(dLon/2))
        b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return round(R * b, round_decimal_digits)

    @staticmethod
    def get_euclidean_distance(x1, y1, x2, y2, round_decimal_digits=5):        
        """
        유클리안 Formula 이용하여 (x1,y1)과 (x2,y2) 점의 거리를 반환
        """
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        assert isinstance(x1, numbers.Number) and -180 <= x1 and x1 <= 180
        assert isinstance(y1, numbers.Number) and  -90 <= y1 and y1 <=  90
        assert isinstance(x2, numbers.Number) and -180 <= x2 and x2 <= 180
        assert isinstance(y2, numbers.Number) and  -90 <= y2 and y2 <=  90

        dLon = abs(x2-x1) # 경도 차이
        if dLon >= 180:   # 반대편으로 갈 수 있는 경우
            dLon -= 360   # 반대편 각을 구한다
        dLat = y2-y1      # 위도 차이
        return round(math.sqrt(pow(dLon,2)+pow(dLat,2)),round_decimal_digits)

    @staticmethod
    def transformCoordinate(_from, _to, coordinate: tuple):
        return transform(_from, _to, *coordinate)
    
    # degrees to radians
    @staticmethod
    def deg2rad(degrees):
        return math.pi*degrees/180.0

    # radians to degrees
    @staticmethod
    def rad2deg(radians):
        return 180.0*radians/math.pi

    # Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
    @staticmethod
    def WGS84EarthRadius(lat):
        # Semi-axes of WGS-84 geoidal reference
        WGS84_a = 6378137.0  # Major semiaxis [m]
        WGS84_b = 6356752.3  # Minor semiaxis [m]

        # http://en.wikipedia.org/wiki/Earth_radius
        An = WGS84_a*WGS84_a * math.cos(lat)
        Bn = WGS84_b*WGS84_b * math.sin(lat)
        Ad = WGS84_a * math.cos(lat)
        Bd = WGS84_b * math.sin(lat)
        return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

    # Bounding box surrounding the point at given coordinates,
    # assuming local approximation of Earth surface as a sphere
    # of radius given by WGS84
    @staticmethod
    def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
        lat = Geo.deg2rad(latitudeInDegrees)
        lon = Geo.deg2rad(longitudeInDegrees)
        halfSide = 1000*halfSideInKm

        # Radius of Earth at given latitude
        radius = Geo.WGS84EarthRadius(lat)
        # Radius of the parallel at given latitude
        pradius = radius*math.cos(lat)

        latMin = lat - halfSide/radius
        latMax = lat + halfSide/radius
        lonMin = lon - halfSide/pradius
        lonMax = lon + halfSide/pradius

        return (Geo.rad2deg(latMin), Geo.rad2deg(lonMin), Geo.rad2deg(latMax), Geo.rad2deg(lonMax))