from datetime import datetime

# from modules.messages_manager import register_number, unregister_number, read_messages, send_message


def add_log_record(status: int, record: str, log_file: str = 'app.log'):
    with open(log_file, 'a', encoding='utf8') as log:
        log.write(f'{datetime.now()}\t{status} {record}\n')


def main():
    pass


if __name__ == '__main__':
    main()
