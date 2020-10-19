from model.user import User

class RoomUser(User):
    def __init__(self, username, password, name, email, phone):
        User.__init__(self, username, password, User.ROOM_USER)
        self.name = name
        self.email = email
        self.phone = phone