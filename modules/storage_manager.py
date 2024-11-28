import json
import os
from messages_manager import read_messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
STORAGE_FILE = os.path.join(STORAGE_DIR, "messages.json")


def init_storage() -> None:
    """
    Initializes the storage directory and json file if they don't exist
    """
    os.makedirs(STORAGE_DIR, exist_ok=True)

    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)


def save_message(messages: dict) -> None:
    """
    Saves a message and its response to the json file

    param messages dict with keys as phone numbers and values are dict of message details

    :return: None
    """
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving messages: {e}")


def get_all_messages() -> dict:
    """
    Gets all stored messages.
    """
    try:
        if not os.path.exists(STORAGE_FILE):
            print(f"Storage file not found. Initializing storage: ")
            init_storage()

        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from storage: {e}. Re-init storage:")
        init_storage()
        return {}
    except IOError as e:
        print(f"Error reading from storage file: {e} ")
        return {}


def save_messages_api(team_name: str) -> None:
    """
    Gets messages from the API and saves them to storage
    dict only, no list wrappers

    :param team_name: Name of team to get the messages
    :return: None
    """
    try:
        status_code, api_messages = read_messages(team_name)

        if status_code != 200:
            print(f"Error: Failed to fetch messages. Status code: {status_code}, Error: {api_messages}")
            return

        if isinstance(api_messages, dict):
            for number, msg_list in api_messages.items():
                if isinstance(msg_list, list):
                    api_messages[number] = msg_list

            if api_messages:
                save_message(api_messages)
        else:
            print(f"Unexpected message format: {api_messages}")
    except Exception as e:
        print(f"Error while fetching or saving messages: {e}")