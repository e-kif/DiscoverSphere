"""
this module should keep track of our users.
we should save
- user phone number
- last selected location
- last selected type of attraction
- list of attractions
- last attraction that we sent to the user
"""

import user_tracker

class User:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.last_location = None
        self.last_attraction_type = None
        self.attractions_list = []
        self.last_sent_attraction = None

    def update_last_location(self, location):
        self.last_location = location

    def update_last_attraction_type(self, attraction_type):
        self.last_attraction_type = attraction_type

    def add_to_attractions_list(self, attraction):
        self.attractions_list.append(attraction)

    def update_last_sent_attraction(self, attraction):
        self.last_sent_attraction = attraction

class UserTracker:
    def __init__(self):
        self.users = {}  # Dictionary to store users by phone number

    def add_user(self, phone_number):
        if phone_number not in self.users:
            self.users[phone_number] = User(phone_number)

    def get_user(self, phone_number):
        return self.users.get(phone_number)

    def update_user_info(self, phone_number, **kwargs):
        user = self.get_user(phone_number)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)