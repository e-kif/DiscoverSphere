import os
from dotenv import load_dotenv
import json
from random import randint


load_dotenv()


def get_random_item(env_key: str) -> str:
    items = json.loads(os.getenv(env_key))
    index = randint(0, len(items) - 1)
    return items[index]


def goodbye_text():
    return get_random_item('farewells')


def welcome_text():
    start = get_random_item('onboards')
    middle = ' Reply with a city of your dreams. Example:\nLOCATION '
    end = get_random_item('cities')
    return start + middle + end


def city_not_found_text():
    return get_random_item('not_found') + get_random_item('cities')


def main():
    print(city_not_found_text())




if __name__ == '__main__':
    main()
