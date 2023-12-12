# app/models.py
from flask_login import UserMixin

class User(UserMixin):
    users = {}  # In-memory storage for users

    def __init__(self, username, access_token):
        self.username = username
        self.access_token = access_token
    
    def get_id(self):
        return self.username

    @classmethod
    def load_user(cls, username):
        return cls.users.get(username)