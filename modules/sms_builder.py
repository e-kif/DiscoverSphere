import os
from dotenv import load_dotenv
import json
from random import randint
import requests


load_dotenv()
ATTRACTIONS_LONG = 'https://raw.githubusercontent.com/e-kif/DiscoverSphere/refs/heads/main/static/attractions_types.json'
ATTRACTIONS = 'https://tinyurl.com/2yyxqodb'


def get_random_item(env_key: str) -> str:
    items = json.loads(os.getenv(env_key))
    index = randint(0, len(items) - 1)
    return items[index]


def get_attractions_list(storage: str = os.path.join('static', 'attractions_types.json')) -> list:
    with open(storage, 'r', encoding='utf8') as file:
        attractions = json.loads(file.read())
    all_attractions = []
    for key, value in attractions.items():
        all_attractions += [key] + value
    return all_attractions


def get_random_attraction_type():
    attractions = get_attractions_list()
    return attractions[randint(0, len(attractions) - 1)]


def make_url_short(url: str):
    request_url = 'https://tinyurl.com/api-create.php?url=' + url
    try:
        response = requests.get(request_url)
    except Exception:
        return url
    if response.status_code != 200:
        return url
    return response.text


def goodbye_text():
    return get_random_item('farewells')


def welcome_text():
    start = get_random_item('onboards')
    middle = ' Reply with a city of your dreams. Example:\nLOCATION '
    end = get_random_item('cities')
    return start + middle + end


def city_not_found_text():
    return get_random_item('not_found') + get_random_item('cities')


def attraction_type_text(location):
    type1 = get_random_attraction_type()
    type2 = get_random_attraction_type()



def main():
    pass


if __name__ == '__main__':
    main()
