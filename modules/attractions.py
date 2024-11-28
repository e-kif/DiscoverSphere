from dotenv import load_dotenv
import requests
import os
from sms_builder import make_url_short
load_dotenv()


def get_api_key():
    """Gets API key from the environment."""
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please check the .env file.")
    return api_key


def geocode_city_finder(city_name, api_key):
    """We are using Geoapify Geocoding API to fetch
        latitude and longitude of a city

        params:
            city_name (str): Name of the city,
            api_key (str): Geoapify API key

        Returns:
            tuple: Lat and Long of the city or None if not found
            """
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": city_name,
        "apiKey": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "features" in data and len(data["features"]) > 0:
            # Fetching first result that matches
            location = data["features"][0]["geometry"]["coordinates"]
            return location[1], location[0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e} ")
        return None


def fetch_attractions(lat, long, radius, attr_type, api_key):
    """Fetch desired attraction creating a unique request
       regarding users likes

    Parameters:
        lat (float): Latitude of the location.
        long (float): Longitude of the location.
        radius (int): Radius for the search in meters.
        attr_type (str): Category of the attraction.
        api_key (str):API key.

    Returns:
        HTTP status code and list of attractions or None
    """
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": attr_type,  # e.g. tourism.attraction or 1.2 in screenshot
        # radius in meters from center. e.g. '5000' for 5km
        "filter": f"circle:{long},{lat},{radius}",
        # results limit
        "limit": 10,
        "apiKey": api_key,
        "lang": "en"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        attractions = data.get("features", [])
        return response.status_code, attractions
    except requests.exceptions.RequestException as e:
        response = requests.get(url, params=params)
        response.raise_for_status()
        if 'apiKey' in str(e):
            print(f"Error: Something unexpected happened while fetching attractions.")
        else:
            print(f"Error: {e}")
        return response.status_code, e


def final_fetch(lat, long, radius, attr_type, api_key):
    """
    Uses the existing fetch_attractions() to process the attractions
    and returns a tuple with code and list of names and short url.

        lat (float): Latitude of the location.
        long (float): Longitude of the location.
        radius (int): Radius for the search in meters.
        attr_type (str): Category of the attraction.
        api_key (str):API key.

    :return: tuple: HTTP status code and list of tuples (name, short url).
    """
    status_code, attractions = fetch_attractions(lat, long, radius, attr_type, api_key)

    if status_code != 200 or not attractions:
        return status_code, []

    results = []
    for attr in attractions:
        # Extract details name and short url
        address_line1 = attr["properties"]["address_line1"]
        coord = attr["geometry"]["coordinates"]
        url_base = "https://www.google.com/maps/place/"
        url_attr = f"{url_base}{coord[1]}{coord[0]}"
        short_url = make_url_short(url_attr)
        if address_line1:
            results.append((address_line1, short_url))

    return status_code, results


def search_and_display(city_name, attraction_type, radius=5000):
    """
    Fetch city coord, search for attractions and return tuple result.

    Params:
    city_name (str): Name of the city (user_provided)
    attraction_type (str): Type of attraction (user_provided)
    radius (int): Search radius in meters (default: 5000 or 5km)

    Returns:
        tuple: HTTP status code, list of attractions or None
    """
    api_key = get_api_key()
    location = geocode_city_finder(city_name, api_key)

    if not location:
        return 404, None  # City not found or Invalid input

    lat, long = location
    # Fetching the attractions
    status_code, attractions = fetch_attractions(lat, long, radius, attraction_type, api_key)

    if not attractions:
        return status_code, None

    return status_code, attractions


def main():
    geo_key = get_api_key()
    lat = 35.6895  # Tokyo Latitude
    lon = 139.6917  # Tokyo Longitude
    radius = 7000
    attr_type = "tourism.attraction"  # Example: Attraction category

    code, attractions = final_fetch(lat, lon, radius, attr_type, geo_key)

    if code == 200 and attractions:
        print("\nAttractions Found in Tokyo:")
        for name, url in attractions:
            print(f"Name: {name}, Shortened URL: {url}")
    else:
        print(f"Failed to fetch attractions in Tokyo. HTTP Status Code: {code}")


# Test this example
if __name__ == "__main__":
    main()
