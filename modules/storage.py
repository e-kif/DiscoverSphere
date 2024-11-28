"""
this module should keep track of our users.
we should save
- user phone number
- last selected location
- last selected type of attraction
- list of attractions
- last attraction that we sent to the user
"""

class UserTracker:
    def __init__(self):
        self.users = {}

    def add_user(self, phone_number):
        if phone_number not in self.users:
            self.users[phone_number] = {
                'last_location': None,
                'last_attraction_type': None,
                'attractions': [],
                'last_sent_attraction': None
            }

    def update_user_info(self, phone_number, **kwargs):
        if phone_number in self.users:
            self.users[phone_number].update(kwargs)

    def get_user_info(self, phone_number):
        if phone_number in self.users:
            return self.users[phone_number]
        else:
            return None
