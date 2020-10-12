from model.room_info import RoomInfo

class Room(RoomInfo):
    def __init__(self, **kwargs):
        super(self, kwargs)
        self.floor = int(kwargs["floor"])
        self.building_floor = int(kwargs["building_floor"])
        self.room_count = int(kwargs["room_count"])
        self.bath_count = int(kwargs["bath_count"])
        self.reg_date = kwargs["reg_date"]
        self.building_date = kwargs["building_date"]
        self.maintain_cost = int(kwargs["maintain_cost"])
        self.options = kwargs["options"]
    
    @staticmethod
    def from_request(form):
        pass