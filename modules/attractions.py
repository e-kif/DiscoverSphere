from dotenv import load_dotenv
import requests
import os
from requests.structures import CaseInsensitiveDict
load_dotenv()


def get_api_key():
    """Gets API key from the environment."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please check the .env file.")
    return api_key


def fetch_attractions():
    pass

    #  fetch attraction places from api given location and attraction type
    #  https://apidocs.geoapify.com/playground/places/

    # test
