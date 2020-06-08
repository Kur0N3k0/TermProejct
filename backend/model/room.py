class Room(object):
    def __init__(self, **kwargs):
        self.is_favorited           = kwargs["is_favorited"]
        self.seq                    = kwargs["seq"]
        self.id                     = kwargs["id"]
        self.user_id                = kwargs["user_id"]
        self.deleted                = kwargs["deleted"]
        self.name                   = kwargs["name"]
        self.title                  = kwargs["title"]
        self.room_type              = kwargs["room_type"]
        self.random_location        = kwargs["random_location"]
        self.geo                    = {
            "type": "Point",
            "coordinates": [ self.random_location[0], self.random_location[1] ]
        }
        self.complex_name           = kwargs["complex_name"]
        self.premium_badge          = kwargs["premium_badge"]
        self.hash_tags              = kwargs["hash_tags"]
        self.room_type_str          = kwargs["room_type_str"]
        self.room_desc              = kwargs["room_desc"]
        self.img_url                = kwargs["img_url"]
        self.img_urls               = kwargs["img_urls"]
        self.is_pano                = kwargs["is_pano"]
        self.price_title            = kwargs["price_title"]
        self.selling_type           = kwargs["selling_type"]
        self.is_confirm             = kwargs["is_confirm"]
        self.confirm_type           = kwargs["confirm_type"]
        self.confirm_date_str       = kwargs["confirm_date_str"]
        self.is_quick               = kwargs["is_quick"]
        self.is_messenger_actived   = kwargs["is_messenger_actived"]
        
        # related with location.code
        self.region_code            = kwargs["region_code"]