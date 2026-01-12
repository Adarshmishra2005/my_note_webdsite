from flask import current_app
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.email = user_dict['email']
        self.first_name = user_dict['first_name']
        self.password = user_dict['password']


