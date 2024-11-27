import os
from dotenv import load_dotenv
from random import randint


def get_random_city():
    cities = os.getenv('cities').split(', ')
    index = randint(0, len(cities) - 1)
    return cities[index]

