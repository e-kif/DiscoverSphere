"""Module interacts with user persistence storage"""
import os
import json


class UserStorage:
    """Class for interaction with user storage"""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = os.path.join(base_dir, "storage", "users.json")

    def __init__(self, storage_filename=filename):
        self.storage_file = storage_filename

    def read_storage(self) -> dict:
        if not os.path.exists(self.storage_file):
            self.write_storage({})
            return {}
        with open(self.storage_file, 'r', encoding='utf8') as file:
            content = file.read()
        if content:
            return json.loads(content)

    def write_storage(self, data: dict):
        with open(self.storage_file, 'w', encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


# todo check if a storage file exists

# todo initiate storage file

# todo check if a storage file empty

# todo user init (phone number: int, location: str, type: str, places: list, index: int)

# todo setters and getters for location, type, places, index


example_struture = {
    'user_number1': {
        'location': 'city name',
        'type': 'attraction type',
        'attractions': 'list of attractions from final_fetch',
        'index': 'int'
    },
    'user_number2': {
        'location': 'city name',
        'type': 'attraction type',
        'attractions': 'list of attractions from final_fetch',
        'index': 'int'
    }
}
