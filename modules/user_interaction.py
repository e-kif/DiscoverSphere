from dotenv import load_dotenv
from datetime import datetime
import os
from random import randint
import re

from modules.messages_manager import register_number, unregister_number, read_messages, send_message
import modules.sms_builder as sms_builder
from modules.storage_manager import save_message, get_all_messages
from modules.attractions import geocode_city_finder, final_fetch
import modules.storage_users as storage_users

from main import DEBUG, SEND_SMS

load_dotenv()
some_phone_number = int(os.getenv('some_number'))
sms_commands = {}
TEAM_NAME = 'Attraction'
LOG_FILENAME = os.path.join('storage', 'app.log')
DEV_LOG = 'app.log'
# SEND_SMS = False
# DEBUG = True


def add_log_record(status: int, record: str, log_file: str = LOG_FILENAME):
    """Adds a record to a log file with date stamp, status code and message"""
    record = ' '.join(record.split('\n'))
    record = re_obfuscate(record)
    with open(log_file, 'a', encoding='utf8') as log:
        log.write(f'{datetime.now()}\t{status} {record}\n')


def re_obfuscate(text: str) -> str:
    patterns = [r'destination":"(\d*)?"',
                r'Number "(\d*)?"',
                r'Error: The number "(\d*)?"']

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            start, end = match.span(1)
            text = text[:start] + '*' * (end - start - 4) + text[end - 4:]
    return text


def obfuscate(func):
    """Function decorator that obfuscates part of the user's phone number for logs"""

    def inner(user_number, text='', team=TEAM_NAME):
        obfuscated_user_number = (len(str(user_number)) - 4) * '*' + str(user_number)[-4:]
        return func(user_number, obfuscated_user_number, text, team)
        # return func(user_number, '', text, team)
    return inner


def get_last_message_time(messages: dict | list) -> datetime:
    """Parses a dict. Returns a datetime object of the very last message from dict"""
    if not messages:
        return datetime(1, 1, 1)
    times = []
    for data in messages.values():
        times.append(max(str_to_datetime(message['receivedAt']) for message in data))
    return max(times) if times else datetime(1, 1, 1)


def str_to_datetime(text: str) -> datetime:
    """Converts a string into datetime object"""
    return datetime.fromisoformat(text.split('+')[0])


def filter_new_messages(old: dict, new: dict | list) -> list:
    """Takes two dicts. Returns a list of messages that are present in new messages
    and are absent in old ones. Logs amount of returned messages.
    Overwrites messages' storage
    """
    if isinstance(new, list) and new:
        new = new[0]
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
    """Parses one message dict and runs corresponding command"""
    for user_number, data in message.items():
        for command in commands:
            if data['text'].startswith(command):
                command, *text = data['text'].strip().split(' ')
                text = ' '.join(text)
                return commands.get(command, commands['DOCS'])(user_number=user_number, text=text)
        text = data['text'].strip()
        return commands['DOCS'](user_number=user_number, text=text)


def user_doesnt_exist(user_number):
    if not storage_users.user_exists(str(user_number)):
        sms_text = sms_builder.subscribe_text()
        if SEND_SMS:
            code, message = send_message(user_number, sms_text)
            return True, (code, message)
        return True, (200, f'user sort of got a message: {sms_text}')
    return False, (200, 'user does exists')


@obfuscate
def subscribe_user(user_number: int,
                   obfuscated_number: str = '',
                   text: str = '',
                   team: str = TEAM_NAME) -> tuple[int, str]:
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
        add_log_record(code, f'User {obfuscated_number} was successfully subscribed to {team}')
        storage_users.init_user(user_number, None, None, None)
        if SEND_SMS:
            sms_text = sms_builder.welcome_text()
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
    add_log_record(code, message)
    return code, message


@obfuscate
def unsubscribe_user(user_number: int,
                     obfuscated_number: str = '',
                     text: str = '',
                     team: str = TEAM_NAME) -> tuple[int, str]:
    """Unregisters user from a team group, sends farewell sms, adds logs"""
    if DEBUG: print(f'removing {user_number} from {team}')
    if text:
        team = text
        text = f' ({text})'
    if not obfuscated_number:
        obfuscated_number = user_number
    add_log_record(100, f'Unsubscribing {obfuscated_number} from "{team}"{text}')
    code, message = unregister_number(user_number)  # todo add a team parameter
    add_log_record(code, message)
    if code == 200:
        if SEND_SMS:
            sms_text = sms_builder.goodbye_text()
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
    return code, message


@obfuscate
def set_location(user_number: int,
                 obfuscated_number: str = '',
                 text: str = '',
                 team: str = TEAM_NAME) -> tuple[int, str]:
    """Checks if location exists, if not - send sms. Saves location to a storage. Sends """
    if DEBUG: print(f'this should set location to {text} for {user_number} ({text=})')
    add_log_record(100, f'Adding location {text} for user {obfuscated_number}')
    wrong_user, message = user_doesnt_exist(user_number)
    if wrong_user:
        add_log_record(404, f'User {obfuscated_number} is not registered')
        return message[0], message[1]
    coords = geocode_city_finder(text, os.getenv('GEOAPIFY_API_KEY'))
    if not coords:
        sms_text = sms_builder.city_not_found_text()
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(f'400 {sms_code}', sms_message + sms_text)
            return f'400 {sms_code}', f'City not found. {sms_message}'
        add_log_record(400, f'user sort of got a messaga: {sms_text}')
        return f'400', f'user sort of got a messaga: {sms_text}'
    storage_users.set_user_attribute(str(user_number), 'location', [text, coords])
    storage_users.set_user_attribute(str(user_number), 'type', None)
    storage_users.set_user_attribute(str(user_number), 'attraction', None)
    sms_text = sms_builder.attraction_type_text(text)
    if SEND_SMS:
        sms_code, sms_message = send_message(user_number, sms_text)
        add_log_record(sms_code, sms_message + sms_text)
        return sms_code, sms_message
    add_log_record(200, f'user sort of got a message: {sms_text}')
    return 200, f'user sort of got a message: {sms_text}'


@obfuscate
def set_attraction_type(user_number: int,
                        obfuscated_number: str = '',
                        text: str = '',
                        team: str = TEAM_NAME) -> tuple[int, str]:
    """Validates attractions type (if not valid - send sms). Saves attraction type to a storage.
    Fetches and a list of attractions. If type is not 'surprise' saves a list of attractions to a storage.
    Sends attraction info to the user. Logs the process."""
    if DEBUG: print(f'this should set attraction type to {text} for {user_number} ({text=})')
    add_log_record(100, f'Adding attraction {text} for {obfuscated_number}')
    wrong_user, message = user_doesnt_exist(user_number)
    if wrong_user:
        add_log_record(404, f'User {obfuscated_number} is not registered')
        return message[0], message[1]
    if not storage_users.get_user_attribute(str(user_number), 'location'):
        sms_text = "Hold your horses! Send text 'LOCATION city' with your destination as a city first."
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        return 200, f'user sort of got a message: {sms_text}'
    api = os.getenv('GEOAPIFY_API_KEY')
    attractions = sms_builder.get_attractions_list()
    if text not in attractions + ['surprise']:
        sms_text = sms_builder.wrong_attraction_text(text)
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got message: {sms_text}')
        return 200, f'user sort of got message: {sms_text}'
    storage_users.set_user_attribute(str(user_number), 'type', text)

    start = 'Your attraction: '
    coords = storage_users.get_user_attribute(str(user_number), 'location')[1]

    if text == 'surprise':
        for _ in range(3):
            text = sms_builder.get_random_attraction_type()
            start = f'Your surprise is {text}\n'
            code, message = final_fetch(coords[0], coords[1], 7000, text, api)
            if code == 200 and message:  # non-empty list
                storage_users.set_user_attribute(str(user_number), 'attraction', message)
                storage_users.set_user_attribute(str(user_number), 'index', 0)
                title, url = message[randint(0, len(message) - 1)]
                sms_text = start + '\n'.join([title, url])
                if SEND_SMS:
                    sms_code, sms_message = send_message(user_number, sms_text)
                    add_log_record(sms_code, sms_message + sms_text)
                    return sms_code, sms_message
                add_log_record(200, f'user sort of got a message: {sms_text}')
                return 200, f'user sort of got a message: {sms_text}'
        sms_text = 'We are out of surprises right now. Try again later or pick another TYPE of attractions'
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got a message: {sms_text}')
        return 200, f'user sort of got a message: {sms_text}'

    code, message = final_fetch(coords[0], coords[1], 7000, text, api)
    if code == 200 and message:  # non-empty list
        storage_users.set_user_attribute(str(user_number), 'attraction', message)
        storage_users.set_user_attribute(str(user_number), 'index', 0)
        if DEBUG: print(code, message)
        title, url = message[0]
        sms_text = start + '\n'.join([title, url])
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got a message: {sms_text}')
        return 200, f'user sort of got a message: {sms_text}'
    elif code == 200:  # empty list
        sms_text = ('We are not able to find something interesting with your LOCATION and TYPE.\n'
                    'Try changing TYPE or LOCATION and TYPE.')
        if SEND_SMS:
            sms_code, sms_message = send_documentation(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got a message: {sms_text}')
        return 200, f'user sort of got a message: {sms_text}'


@obfuscate
def send_next_attraction(user_number: int,
                         obfuscated_number: str = '',
                         text: str = '',
                         team: str = TEAM_NAME) -> tuple[int, str]:
    """Gets user info from a storage, sends nex attraction that corresponds to previous user's requests"""
    if DEBUG: print(f'this should send next attraction to {user_number} ({text=})')
    add_log_record(100, f'Sending next attraction to {obfuscated_number}')
    wrong_user, message = user_doesnt_exist(user_number)
    if wrong_user:
        add_log_record(404, f'User {obfuscated_number} is not registered')
        return message[0], message[1]
    location = storage_users.get_user_attribute(str(user_number), 'location')
    attr_type = storage_users.get_user_attribute(str(user_number), 'type')
    if attr_type == 'surprise':
        coords = storage_users.get_user_attribute(str(user_number), 'location')[1]
        for _ in range(3):
            text = sms_builder.get_random_attraction_type()
            start = f'Your surprise is {text}\n'
            code, message = final_fetch(coords[0], coords[1], 7000, text, os.getenv('GEOAPIFY_API_KEY'))
            if code == 200 and message:  # non-empty list
                storage_users.set_user_attribute(str(user_number), 'attraction', message)
                storage_users.set_user_attribute(str(user_number), 'index', 0)
                title, url = message[randint(0, len(message) - 1)]
                sms_text = start + '\n'.join([title, url])
                if SEND_SMS:
                    sms_code, sms_message = send_message(user_number, sms_text)
                    add_log_record(sms_code, sms_message + sms_text)
                    return sms_code, sms_message
                add_log_record(200, f'user sort of received a message: {sms_text}')
                return 200, f'user sort of received a message: {sms_text}'
        sms_text = ('We are out of surprises right now. Try again later or pick another TYPE of attractions: '
                    'https://tinyurl.com/2yyxqodb')
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of received a message: {sms_text}')
        return 200, f'user sort of received a message: {sms_text}'
    attractions = storage_users.get_user_attribute(str(user_number), 'attraction')
    index = storage_users.get_user_attribute(str(user_number), 'index')
    if not attractions:
        missing = ''
        if not attr_type:
            missing = "'TYPE newtype' with desired attractions type. Get inspired here: https://tinyurl.com/2yyxqodb"
        if not location:
            missing = "'LOCATION city' with your destination as a city first."
        sms_text = f'Hold your horses! Send text {missing}'
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got a message: {sms_text}')
        return 200, f'user sort of got a message: {sms_text}'
    if index + 1 == len(attractions):
        sms_text = sms_builder.newtype_text()
        if SEND_SMS:
            sms_code, sms_message = send_message(user_number, sms_text)
            add_log_record(sms_code, sms_message + sms_text)
            return sms_code, sms_message
        add_log_record(200, f'user sort of got a message: {sms_text}')
        return 200, f'user sort of got a message: {sms_text}'
    sms_text = '\n'.join(attractions[index + 1])
    if DEBUG: print(sms_text)
    if SEND_SMS:
        sms_code, sms_message = send_message(user_number, sms_text)
        if sms_code == 200:
            storage_users.set_user_attribute(str(user_number), 'index', index + 1)
        add_log_record(sms_code, sms_message + sms_text)
        return sms_code, sms_message
    storage_users.set_user_attribute(str(user_number), 'index', index + 1)
    add_log_record(200, f'user sort of got a message: {sms_text}')
    return 200, f'user sort of got a message: {sms_text}'


@obfuscate
def send_documentation(user_number: int,
                       obfuscated_number: str = '',
                       text: str = '',
                       team: str = TEAM_NAME) -> tuple[int, str]:
    """Sends sms to a user with available commands"""
    if DEBUG: print(f'this should send docs to {user_number} ({text=})')
    add_log_record(100, f'Sending docs to {obfuscated_number}')
    sms_text = ("We get: 'SUBSCRIBE Attraction', 'UNSUBSCRIBE Attraction', 'LOCATION Q', 'TYPE X', 'MORE', 'DOCS'."
                "Q - your destination. X options: https://tinyurl.com/2yyxqodb")
    if SEND_SMS:
        sms_code, sms_message = send_message(user_number, sms_text)
        add_log_record(sms_code, sms_message + sms_text)
        return sms_code, sms_message
    add_log_record(200, f'user sort of got a message: {sms_text}')
    return 200, f'user sort of got a message: {sms_text}'


def get_received_messages_api(team: str = 'Attraction') -> tuple[int, str]:
    add_log_record(100, "Getting messages from Masterschool's SMS API")
    code, message = read_messages(team)
    if code == 200:
        add_log_record(code, 'Messages were successfully collected.')
        if isinstance(message, list) and not message:
            message = {}
        return code, message


sms_commands.update({
    'SUBSCRIBE': subscribe_user,
    'UNSUBSCRIBE': unsubscribe_user,
    'LOCATION': set_location,
    'TYPE': set_attraction_type,
    'MORE': send_next_attraction,
    'DOCS': send_documentation
})


def ux_tests():
    """Function for testing module's functions without importing them"""

    test_messages = [{some_phone_number: {'text': 'MORE', 'receivedAt': '2024-11-27T09:32:59.322+0000'}}]
    test_message = test_messages[0]
    # subscribe_user(some_phone_number)
    # unsubscribe_user(some_phone_number)
    # code1, messages1 = read_messages('TeamABC')
    # code2, messages2 = read_messages('WaterProof')
    code, message = process_new_message(test_message)
    print(f'{code=}')
    print(f'{message=}')


    pass


if __name__ == '__main__':
    ux_tests()
