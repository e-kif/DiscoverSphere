import json
import os
# from datetime import datetime
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

    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=4)


def get_all_messages() -> dict:
    """
    Gets all stored messages.

    :return: dict : Keys are message ID and values are details of messages
    """
    with open(STORAGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_messages_api(team_name: str) -> None:
    """
    Gets messages from the API and saves them to storage
    dict only, no list wrappers

    :param team_name: Name of team to get the messages
    :return: None
    """
    api_messages = read_messages(team_name)

    if isinstance(api_messages, dict):
        refactored_messages = {}

        for number, msg_list in api_messages.items():
            if isinstance(msg_list, list):
                for message in msg_list:
                    refactored_messages[number] = message

        if refactored_messages:
            save_message(refactored_messages)


"""def get_message_by_id(message_id: int) -> dict:
    """"""
    Retrieves targeted messages by ID

    :param message_id:  ID of the targeted message to retrieve

    :return: dict: dictionary with message details for target id
                    if id is invalid, returns empty dictionary
    """"""
    with open(STORAGE_FILE, "r", encoding="utf-8") as file:
        messages = json.load(file)

    return messages.get(str(message_id), {})
""""""

""""""def get_messages_by_number(phone_number: str) -> dict:
    """"""
    Retrieves targeted messages by phone number.

    :param phone_number: Target phone number to retrieve messages

    :return: dict: A dictionary with ID as Keys and values are details
    """"""
    with open(STORAGE_FILE, "r", encoding="utf-8") as file:
        messages = json.load(file)

        # Dict comprehension ** One line dict maker
    return {k: v for k, v in messages.items() if v["phone_number"] == phone_number}
"""
