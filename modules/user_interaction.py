from dotenv import load_dotenv
from datetime import datetime
import json
import os
from random import randint
import requests

from modules.messages_manager import register_number, unregister_number, read_messages, send_message
from modules.sms_builder import welcome_text, goodbye_text, city_not_found_text

load_dotenv()
some_phone_number = int(os.getenv('some_number'))
sms_commands = {}
TEAM_NAME = 'Attraction'
LOG_FILENAME = os.path.join('..', 'storage', 'app.log')
DEV_LOG = 'app.log'


def add_log_record(status: int, record: str, log_file: str = DEV_LOG):
    with open(log_file, 'a', encoding='utf8') as log:
        log.write(f'{datetime.now()}\t{status} {record}\n')


def subscribe_user(user_number: int, text: str = '', team: str = TEAM_NAME) -> int:
    if text:
        text = f' ({text})'
    add_log_record(100, f'Subscribing number {user_number} to {team} group{text}')
    code, message = register_number(user_number)
    if code == 200:
        add_log_record(code, f'User {user_number} was successfully subscribed to {team}')
        sms_text = welcome_text()
        # sms_code, sms_message = send_message(user_number, sms_text)
        # add_log_record(sms_code, sms_message)
        # TODO add new user to persistent storage
        # return sms_code
    add_log_record(code, message)
    return code


def unsubscribe_user(user_number: int, text: str = '', team: str = TEAM_NAME) -> int:
    if text:
        text = f' ({text})'
    add_log_record(100, f'Unsubscribing {user_number} from "{team}"{text}')
    code, message = unregister_number(user_number)
    add_log_record(code, message)
    if code == 200:
        sms_text = goodbye_text()
        # sms_code, sms_message = send_message(user_number, sms_text)
        # add_log_record(sms_code, sms_message)
        # return sms_code
    add_log_record(code, message)
    return code


def set_location():
    # TODO implement
    pass


def set_attraction_type():
    # TODO implement
    pass


def send_next_attraction():
    # TODO implement
    pass


def send_documentation():
    # TODO implement
    pass


sms_commands.update({
    'SUBSCRIBE': subscribe_user,
    'UNSUBSCRIBE': unsubscribe_user,
    'LOCATION': set_location,
    'TYPE': set_attraction_type,
    'MORE': send_next_attraction,
    'DOCS': send_documentation
})





def main():
    subscribe_user(some_phone_number)
    unsubscribe_user(some_phone_number)


if __name__ == '__main__':
    main()
