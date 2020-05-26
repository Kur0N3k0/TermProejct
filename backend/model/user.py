import uuid

class User(object):
    USER = 0
    ROOM_USER = 1
    ADMIN = 2

    def __init__(self, username, password, level: int = USER):
        self.username = username
        self.password = password
        self.level = level