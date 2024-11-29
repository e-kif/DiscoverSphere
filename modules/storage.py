"""
this module should keep track of our users.
we should save
- user phone number
- last selected location
- last selected type of attraction
- list of attractions
- last attraction that we sent to the user
"""

import json

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

    def to_dict(self):
        return {
            "phone_number": self.phone_number,
            "last_location": self.last_location,
            "last_attraction_type": self.last_attraction_type,
            "attractions_list": self.attractions_list,
            "last_sent_attraction": self.last_sent_attraction
        }

class UserTracker:
    def __init__(self, filename="user_data.json"):
        self.filename = filename
        self.users = {}
        self.load_users()

    def load_users(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for user_data in data:
                    user = User(user_data['phone_number'])
                    for key, value in user_data.items():
                        setattr(user, key, value)
                    self.users[user.phone_number] = user
        except FileNotFoundError:
            pass  # File doesn't exist, create a new one

    def save_users(self):
        user_data = [user.to_dict() for user in self.users.values()]
        with open(self.filename, 'w') as f:
            json.dump(user_data, f, indent=4)

    def add_user(self, phone_number):
        if phone_number not in self.users:
            self.users[phone_number] = User(phone_number)
            self.save_users()

    def get_user(self, phone_number):
        return self.users.get(phone_number)

    def update_user_info(self, phone_number, **kwargs):
        user = self.get_user(phone_number)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.save_users()
