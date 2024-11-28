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
    """Adds a record to a log file with date stamp, status code and message"""
    with open(log_file, 'a', encoding='utf8') as log:
        log.write(f'{datetime.now()}\t{status} {record}\n')


def obfuscate(func):
    """Function decorator that obfuscates part of the user's phone number for logs"""
    def inner(user_number, text='', team=TEAM_NAME):
        obfuscated_user_number = (len(str(user_number)) - 4) * '*' + str(user_number)[-4:]
        return func(user_number, obfuscated_user_number, text, team)
        # return func(user_number, '', text, team)

    return inner


def get_last_message_time(messages: dict) -> datetime:
    """Parses a dict. Returns a datetime object of the very last message from dict"""
    times = []
    for data in messages.values():
        times.append(max(str_to_datetime(message['receivedAt']) for message in data))
    return max(times)


def str_to_datetime(text: str) -> datetime:
    """Converts a string into datetime object"""
    return datetime.fromisoformat(text.split('+')[0])


def get_new_messages(old: dict, new: dict) -> list:
    """Takes two dicts. Returns a list of messages that are present in new messages
    and are absent in old ones. Logs amount of returned messages.
    Overwrites messages' storage
    """
    old_last_message = get_last_message_time(old)
    new_last_message = get_last_message_time(new)
    if new_last_message == old_last_message:
        return []
    new_messages = []
    for number, messages in new.items():
        new_messages += [{number: message}
                         for message in sorted(messages, key=lambda a: str_to_datetime(a['receivedAt']))
                         if str_to_datetime(message['receivedAt']) > old_last_message]
    add_log_record(102, f'Found {len(new_messages)} new messages. Processing...')
    # todo write new dict to storage
    return new_messages


def process_new_message(message: dict, commands: dict = sms_commands):
    """Parses every message and runs corresponding command"""
    for user_number, data in message.items():
        for command in commands:
            if data['text'].startswith(command):
                command, *text = data['text'].strip().split(' ')
                text = ' '.join(text)
                return commands.get(command, commands['DOCS'])(user_number, text)
        text = data['text'].strip()
        print(f'{text=}')
        return commands['DOCS'](user_number, text)


@obfuscate
def subscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    """Adds user to a team group, adds user info to a storage,
    sends welcome sms that asks for location, adds some logs.
    """
    if text:
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = str(user_number)
    add_log_record(100, f'Subscribing number {obfuscated_number} to {team} group{text}')
    code, message = register_number(user_number)
    if code == 200:
        add_log_record(code, f'User {user_number} was successfully subscribed to {team}')
        # sms_text = welcome_text()
        # sms_code, sms_message = send_message(user_number, sms_text)
        # add_log_record(sms_code, sms_message)
        # TODO add new user to persistent storage (set location, type, index to none)
        # return sms_code
    add_log_record(code, message)
    return code


@obfuscate
def unsubscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    """Unregisters user from a team group, sends farewell sms, adds logs"""
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


def set_location(user_number: int,
                 obfuscated_number: str = '',
                 text: str = '',
                 team: str = TEAM_NAME) -> (int, str):
    """Checks if location exists, if not - send sms. Saves location to a storage. Sends """
    # todo if location exists (send message if not)
    # todo save location info to a storage
    # todo empty type and index in storage
    # todo generate sms request for types
    # todo log the process

    # code, message = send_message(user_number, sms_text)
    # return code, message

    pass


def set_attraction_type(user_number: int,
                        obfuscated_number: str = '',
                        text: str = '',
                        team: str = TEAM_NAME) -> (int, str):
    """Validates attractions type (if not valid - send sms). Saves attraction type to a storage.
    Fetches and a list of attractions. If type is not 'surprise' saves a list of attractions to a storage.
    Sends attraction info to the user. Logs the process."""
    # todo validate attraction type (send sms if false)
    # todo write type to a storage
    # todo read location from storage
    # todo fetch attractions
    # todo implement surprise type
    # todo write attractions to a storage
    # todo send sms
    # todo write attraction index to a storage
    # todo log the process
    pass


def send_next_attraction(user_number: int,
                         obfuscated_number: str = '',
                         text: str = '',
                         team: str = TEAM_NAME) -> (int, str):
    """Gets user info from a storage, sends nex attraction that corresponds to previous user's requests"""
    # todo read location info from a storage
    # todo read type info from a storage
    # todo read index from a storage
    # todo read next attraction from storage
    # todo send sms
    # todo save new index to storage
    # todo log the process
    pass


def send_documentation(user_number: int,
                       obfuscated_number: str = '',
                       text: str = '',
                       team: str = TEAM_NAME) -> (int, str):
    """Sends sms to a user with available commands"""
    # todo generate/read text
    # todo send sms
    # todo log the process
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
    """Function for testing module's functions without importing them"""
    # subscribe_user(some_phone_number)
    # unsubscribe_user(some_phone_number)
    pass


if __name__ == '__main__':
    main()
