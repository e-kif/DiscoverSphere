from dotenv import load_dotenv
from datetime import datetime
import os

from modules.messages_manager import register_number, unregister_number, read_messages, send_message

load_dotenv()
some_phone_number = int(os.getenv('some_number'))
sms_commands = {}
TEAM_NAME = 'Attraction'


def add_log_record(status: int, record: str, log_filename: str = os.path.join('..', 'storage', 'app.log')):
    with open(log_filename, 'a', encoding='utf8') as log:
        log.write(f'{datetime.now()}\t{status} {record}\n')


def subscribe_user(user_number: int, text: str = '', team: str = TEAM_NAME) -> int:
    add_log_record(100, f'Subscribing number {user_number} to {text} group')
    code, message = register_number(user_number)
    if code == 200:
        add_log_record(code, f'User {user_number} was successfully subscribed for {team}')
        loc_keyword = list(sms_commands.keys())[2]
        welcome_text = ('Welcome to the DiscoverSphere app!\n'
                        f'To set your destination reply to this SMS with keyword {loc_keyword} '
                        f'followed by a city. Example:\n{loc_keyword} Berlin')
        sms_code, sms_message = send_message(user_number, welcome_text)
        add_log_record(sms_code, sms_message)
        # TODO add new user to persistent storage
        return sms_code
    add_log_record(code, message)
    return code


def unsubscribe_user(user_number: int, text: str, team: str = TEAM_NAME) -> int:
    add_log_record(100, f'Unsubscribing {user_number} from {team} ({text})')
    code, message = unregister_number(user_number)
    add_log_record(code, message)
    if code == 200:
        # TODO send unsubscribe confirmation sms
        return code
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
    'SUBSCRIBE': ['SUBSCRIBE', subscribe_user],
    'UNSUBSCRIBE': ['UNSUBSCRIBE', unsubscribe_user],
    'LOCATION': ['LOCATION', set_location],
    'TYPE': ['TYPE', set_attraction_type],
    'MORE': ['MORE', send_next_attraction],
    'DOCS': ['DOCS', send_documentation]
})


def main():
    subscribe_user(some_phone_number)


if __name__ == '__main__':
    main()
