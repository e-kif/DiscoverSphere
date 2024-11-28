"""Module interacts with user persistence storage"""
import os
import json
from attractions import final_fetch, get_api_key


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
STORAGE_FILE = os.path.join(STORAGE_DIR, "users.json")


def init_storage() -> None:
    """
    Initializes the storage directory and json file if they don't exist
    """
    os.makedirs(STORAGE_DIR, exist_ok=True)

    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)


def load_user() -> dict:
    """
    Loads user for storage.

    :return: Dict of users or empty dict if file corrupted or doesn't exist
    """
    if not os.path.exists(STORAGE_FILE):
        init_storage()
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding json: {e}, trying to re-init storage: ")
        init_storage()
        return {}


def save_user(user: dict) -> None:
    """
    Saves the users dict to the storage file.

    :param user: dict of users to save
    :return: None
    """
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump(user, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving users : {e}")


def user_exists(phone_number: str) -> bool:
    """
    Checks if user exists in storage

    :param phone_number: User phone_number
    :return: True if user exist, False if not.
    """
    users = load_user()
    return phone_number in users


def init_user(phone_number, location: str = '', attr_type: str = '',
              attractions: str = '', index: int = 0) -> None:
    """
    Init a user to the storage

    :param phone_number: User's phone number
    :param location: User's city name
    :param attr_type: Type of attractions
    :param attractions: List of attractions
    :param index: Starting index (0)
    """
    users = load_user()

    if not user_exists(phone_number):
        # Add the user to storage
        users[phone_number] = {
            "location": location,
            "type": attr_type,
            "attraction": attractions,
            "index": index
        }
        save_user(users)
    else:
        print(f"User with phone number {phone_number} already exists. ")


def get_user(phone_number: str) -> dict:
    """
    Gets user data from storage

    :param phone_number: User's phone number

    :return: Dictonary of user's data or None if user doesn't exist.
    """
    users = load_user()
    return users.get(phone_number)


def set_user_attribute(phone_number: str, attribute: str, value) -> None:
    """
    Setter for user's attribute
    
    :param phone_number: User's phone number
    :param attribute: Attribute to update('location, 'type', 'attractions', 'index')
    :param value: New value for the attribute
    """
    users = load_user()
    if user_exists(phone_number):
        users[phone_number][attribute] = value
        save_user(users)
    else:
        print(f"User {phone_number} doesn't exist. Check again")


def get_user_attribute(phone_number: str, attribute: str):
    """
    Getter for user's attribute

    :param phone_number: User's phone_number
    :param attribute: Attribute to get ('location', 'type', 'attraction', 'index')
    :return Value of the attribute or None if user/Attribute doesn't exist.
    """

    user = get_user(phone_number)
    if user:
        return user.get(attribute)
    print(f"Attribute {attribute} not found for user {phone_number}")
    return None


# Example Usage!!!
def main():
    # Example `final_fetch` usage to get attractions
    status_code, attractions = final_fetch(lat=35.6895, long=139.6917, radius=5000, attr_type="tourism.attraction",
                                           api_key=get_api_key())

    # Only proceed if attractions are successfully fetched
    if status_code == 200:
        init_user(
            phone_number="1234567894",
            location="Tokyo",
            attr_type="tourism.attraction",
            attractions=attractions
        )
    else:
        return f"Failed to fetch attractions. HTTP Status Code: {status_code}"

    # Fetch user data
    user_data = get_user("1234567890")
    return user_data


if __name__ == "__main__":
    main()


# todo check if a storage file exists

# todo initiate storage file

# todo check if a storage file empty

# todo user init (phone number: int, location: str, type: str, places: list, index: int)

# todo setters and getters for location, type, places, index

"""
example_struture = {
    'user_number1': {  # phone number
        'location': 'city name',  # city name
        'type': 'attraction type',  # attr_type
        'attractions': 'list of attractions from final_fetch',  # tuple of final_fetch() in attractions.py
        'index': 'int'  # default 0
    },
    'user_number2': {
        'location': 'city name',
        'type': 'attraction type',
        'attractions': 'list of attractions from final_fetch',
        'index': 'int'
    }
}
"""