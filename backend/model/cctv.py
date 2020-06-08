class CCTV(object):
    def __init__(self, **kwargs):
        self.manager_name       = kwargs["manager_name"]
        self.camera_count       = kwargs["camera_count"]
        if "address" in kwargs:
            self.address        = kwargs["address"]
        else:
            self.address        = kwargs["address_code"]
        
        if "setup_purpose" in kwargs:
            self.setup_purpose      = kwargs["setup_purpose"]

        self.camera_count       = kwargs["camera_count"]
        if "camera_pixel" in kwargs:
            self.camera_pixel       = kwargs["camera_pixel"]
            
        if "capture_area" in kwargs:
            self.capture_area       = kwargs["capture_area"]

        if "save_limit" in kwargs:
            self.save_limit         = kwargs["save_limit"]

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

        if "provider_code" in kwargs:
            self.provider_code      = kwargs["provider_code"]
        
        if "provider" in kwargs:
            self.provider           = kwargs["provider"]
        