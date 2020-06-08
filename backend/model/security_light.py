class SecurityLight(object):
    def __init__(self, **kwargs):
        self.location_name      = kwargs["location_name"]
        self.setup_count        = kwargs["setup_count"]
        if "address" in kwargs:
            self.address        = kwargs["address"]
        else:
            self.address        = kwargs["address_code"]
        
        self.latitude           = float(kwargs["latitude"])
        self.longtitude         = float(kwargs["longtitude"])
        self.geo                = {
            "type": "Point",
            "coordinates": [ self.longtitude, self.latitude ]
        }
        if "setup_year" in kwargs:
            self.setup_year     = kwargs["setup_year"]
        
        if "setup_figure" in kwargs:
            self.setup_figure   = kwargs["setup_figure"]
        self.manager_tel        = kwargs["manager_tel"]
        self.manager_name       = kwargs["manager_name"]
        self.date               = kwargs["date"]
        self.provider_code      = kwargs["provider_code"]
        self.provider           = kwargs["provider"]
        