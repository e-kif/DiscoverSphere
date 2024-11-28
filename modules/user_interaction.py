from dotenv import load_dotenv
from datetime import datetime
import os

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


def obfuscate(func):
    def inner(user_number, text='', team=TEAM_NAME):
        obfuscated_user_number = (len(str(user_number)) - 4) * '*' + str(user_number)[-4:]
        return func(user_number, obfuscated_user_number, text, team)
        # return func(user_number, '', text, team)
    return inner


@obfuscate
def subscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    if text:
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = str(user_number)
    add_log_record(100, f'Subscribing number {obfuscated_number} to {team} group{text}')
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


@obfuscate
def unsubscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    if text:
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = user_number
    add_log_record(100, f'Unsubscribing {obfuscated_number} from "{team}"{text}')
    code, message = unregister_number(user_number)
    add_log_record(code, message)
    if code == 200:
        sms_text = goodbye_text()
        # sms_code, sms_message = send_message(user_number, sms_text)
        # add_log_record(sms_code, sms_message)
        # return sms_code
    add_log_record(code, message)
    return code


def set_location(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME):
    # todo save location info to storage
    # todo generate sms request for types

    # code, message = send_message(user_number, sms_text)
    # return code, message

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
    # subscribe_user(some_phone_number)
    # unsubscribe_user(some_phone_number)
    subscribe_user(123)


if __name__ == '__main__':
    main()
