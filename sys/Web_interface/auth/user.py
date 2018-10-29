# -*- coding: utf-8 -*-
# Author: swstorage

class User():
    def __init__(self, username):
        self.id = username
    
    # The following 4 methods are required by Flask-Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
