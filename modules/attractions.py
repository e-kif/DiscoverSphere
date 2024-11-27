from dotenv import load_dotenv
import requests
import os
load_dotenv()


def get_api_key():
    """Gets API key from the environment."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please check the .env file.")
    return api_key


def fetch_attractions(lat, long, radius, attr_type, api_key):
    """Fetch desired attraction creating a unique request
       regarding users likes
        """
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": attr_type,
        "filter": f"circle:{long},{lat},{radius}",
        "limit": 10,
        "apiKey": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("features", [])
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def displayer(attractions):
    """Display a list of attraction to the user"""
    if not attractions:
        return False, f"No Attractions found with given Info."

    print("\nAttractions found: ")

    for attraction in attractions:
        name = attraction["properties"].get("name", "unnamed")
        category = attraction["properties"].get("categories", [])
        return True, f"Name :{name}, Categories: {category}"

    #  fetch attraction places from api given location and attraction type
    #  https://apidocs.geoapify.com/playground/places/

    # test
