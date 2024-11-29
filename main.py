import time

import modules.user_interaction as ux
from modules.storage_manager import get_all_messages as get_storage_messages

DEBUG = False
SEND_SMS = True
TIMEOUT = 20


def main():
    """Main function loop that fetches messages from Masterschool API,
    compares them against stored messages. Processes new messages if found"""
    while True:
        code, api_messages = ux.get_received_messages_api()
        if code == 200:
            storage_messages = get_storage_messages()
            new_messages = ux.filter_new_messages(storage_messages, api_messages)
            if new_messages:
                for message in new_messages:
                    ux.process_new_message(message)

        time.sleep(TIMEOUT)


if __name__ == '__main__':
    main()
