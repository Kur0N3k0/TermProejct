class Location(object):
    def __init__(self, **kwargs):
        self.type                   = kwargs["type"]
        self.code                   = kwargs["code"]
        self.id                     = kwargs["id"]
        self.name                   = kwargs["name"]
        self.full_name              = kwargs["full_name"]
        self.zoom                   = kwargs["zoom"]
        self.location               = kwargs["location"]
        self.geo                    = {
            "type": "Point",
            "coordinates": [ self.location[0], self.location[1] ]
        }
        self.bbox                   = kwargs["bbox"]
        self.region                 = kwargs["region"]
        self.radius                 = kwargs["radius"]
        self.line                   = kwargs["line"]
        self.geojson                = kwargs["geojson"]
        self.complex_id             = kwargs["complex_id"]
        self.complex_type_str       = kwargs["complex_type_str"]
        self.complex_address        = kwargs["complex_address"]
        self.filter                 = kwargs["filter"]
        self.subways                = kwargs["subways"]
        