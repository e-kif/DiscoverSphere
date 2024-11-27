from datetime import datetime
import os

from modules.messages_manager import register_number, unregister_number, read_messages, send_message


sms_commands = {}
TEAM_NAME = 'Attraction'


def add_log_record(status: int, record: str, log_filename: str = os.path.join('..', 'storage', 'app.log')):
    if os.path.exists(log_filename):
        with open(log_filename, 'a', encoding='utf8') as log:
            log.write(f'{datetime.now()}\t{status} {record}\n')
    else:
        with open(log_filename, 'w+', encoding='utf8') as log:
            log.write(f'{datetime.now()}\t{status} {record}\n')


def subscribe_user(user_number: int, text: str, team: str = TEAM_NAME) -> int:
    add_log_record(100, f'Subscribing number {user_number} to {text} group')
    # code, message = register_number(user_number)
    # if code == 200:
    #     add_log_record(code, f'User {user_number} was successfully unsubscribed from {team}')
    #     TODO send welcome sms
    #     TODO add new user to persistent storage
    #     return code
    # add_log_record(code, message)
    # return code
    pass


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
    'SUBSCRIBE': subscribe_user,
    'UNSUBSCRIBE': unsubscribe_user,
    'LOCATION': set_location,
    'TYPE': set_attraction_type,
    'MORE': send_next_attraction,
    'UNSUPPORTED': send_documentation
})


def main():
    add_log_record(200, 'Log test')


if __name__ == '__main__':
    main()
