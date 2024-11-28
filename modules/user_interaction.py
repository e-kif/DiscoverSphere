from dotenv import load_dotenv
from datetime import datetime
import os

from modules.messages_manager import register_number, unregister_number, read_messages, send_message
from modules.sms_builder import welcome_text, goodbye_text, city_not_found_text, attraction_type_text
from modules.storage_manager import save_message, get_all_messages
from modules.attractions import geocode_city_finder

load_dotenv()
some_phone_number = int(os.getenv('some_number'))
sms_commands = {}
TEAM_NAME = 'Attraction'
LOG_FILENAME = os.path.join('..', 'storage', 'app.log')
DEV_LOG = 'app.log'
SEND_SMS = False
DEBUG = True


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


def filter_new_messages(old: dict, new: dict) -> list:
    """Takes two dicts. Returns a list of messages that are present in new messages
    and are absent in old ones. Logs amount of returned messages.
    Overwrites messages' storage
    """
    if old:
        old_last_message = get_last_message_time(old)
    else:
        old_last_message = datetime(1, 1, 1)
    new_last_message = get_last_message_time(new)
    if new_last_message == old_last_message:
        return []
    new_messages = []
    for number, messages in new.items():
        new_messages += [{number: message}
                         for message in sorted(messages, key=lambda a: str_to_datetime(a['receivedAt']))
                         if str_to_datetime(message['receivedAt']) > old_last_message]
    add_log_record(102, f'Found {len(new_messages)} new messages. Processing...')
    save_message(new)
    return new_messages


def process_new_message(message: dict, commands: dict = sms_commands):
    """Parses every message and runs corresponding command"""
    for user_number, data in message.items():
        for command in commands:
            if data['text'].startswith(command):
                command, *text = data['text'].strip().split(' ')
                text = ' '.join(text)
                return commands.get(command, commands['DOCS'])(user_number=user_number, text=text)
        text = data['text'].strip()
        return commands['DOCS'](user_number=user_number, text=text)


@obfuscate
def subscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    """Adds user to a team group, adds user info to a storage,
    sends welcome sms that asks for location, adds some logs.
    """
    if DEBUG: print(f'subscribing {user_number} to {team} ({text=})')
    if text:
        team = text
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = str(user_number)
    add_log_record(100, f'Subscribing number {obfuscated_number} to {team} group{text}')
    code, message = register_number(user_number) # todo add a team as parameter
    if code == 200:
        add_log_record(code, f'User {user_number} was successfully subscribed to {team}')
        # TODO add new user to persistent storage (set location, type, index to none)
        if SEND_SMS:
            sms_text = welcome_text()
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message)
            return sms_code
    add_log_record(code, message)
    return code


@obfuscate
def unsubscribe_user(user_number: int, obfuscated_number: str = '', text: str = '', team: str = TEAM_NAME) -> int:
    """Unregisters user from a team group, sends farewell sms, adds logs"""
    if DEBUG: print(f'removing {user_number} from {team}')
    if text:
        team = text
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = user_number
    add_log_record(100, f'Unsubscribing {obfuscated_number} from "{team}"{text}')
    code, message = unregister_number(user_number) # todo add a team parameter
    add_log_record(code, message)
    if code == 200:
        if SEND_SMS:
            sms_text = goodbye_text()
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message)
            return sms_code
    return code


def set_location(user_number: int,
                 obfuscated_number: str = '',
                 text: str = '',
                 team: str = TEAM_NAME) -> (int, str):
    """Checks if location exists, if not - send sms. Saves location to a storage. Sends """
    if DEBUG: print(f'this should set location to {text} for {user_number} ({text=})')
    coords = geocode_city_finder(text, os.getenv('GEOAPIFY_API_KEY'))
    if not coords:
        sms_text = city_not_found_text()
        if DEBUG: print(sms_text)
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            return f'400 {sms_code}', f'City not found. {sms_message}'
    # todo save location info to a storage
    # todo empty type and index in storage
    sms_text = attraction_type_text(text)
    if DEBUG: print(f'sending message: {sms_text}')
    if SEND_SMS:
        sms_code, sms_message = send_message(user_number, sms_text)
        return sms_code, sms_message

    # todo log the process
    return coords


def set_attraction_type(user_number: int,
                        obfuscated_number: str = '',
                        text: str = '',
                        team: str = TEAM_NAME) -> (int, str):
    """Validates attractions type (if not valid - send sms). Saves attraction type to a storage.
    Fetches and a list of attractions. If type is not 'surprise' saves a list of attractions to a storage.
    Sends attraction info to the user. Logs the process."""
    if DEBUG: print(f'this should set attraction type to {text} for {user_number} ({text=})')
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
    if DEBUG: print(f'this should send next attraction to {user_number} ({text=})')
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
    if DEBUG: print(f'this should send docs to {user_number} ({text=})')
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

    test_messages = [{'123': {'text': 'LOCATION Frankfurt', 'receivedAt': '2024-11-27T09:32:59.322+0000'}}]
    test_message = test_messages[0]
    # subscribe_user(some_phone_number)
    # unsubscribe_user(some_phone_number)
    # code1, messages1 = read_messages('TeamABC')
    # code2, messages2 = read_messages('WaterProof')
    coords = process_new_message(test_message)
    print(f'{coords=}')


    pass


if __name__ == '__main__':
    main()
