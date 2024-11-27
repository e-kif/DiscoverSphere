from dotenv import load_dotenv
import requests
import os
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
            print(f"City '{city_name}' not found,")
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
        "apiKey": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return response.status_code, data.get("features", [])
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return 500, None


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

# Testing example, yevhen you can delete after usage


if __name__ == "__main__":
    # Example inputs from User
    city = "Kiev"
    attraction_category = "tourism_attraction"

    # Call the search_and_display function with example inputs
    status, result = search_and_display(city, attraction_category, radius=5000)

    if status == 200 and result:
        print("\nAttractions found: ")
        # API results, use those
        for attraction in result:
            name = attraction["properties"].get("name", "unnamed")
            category = attraction["properties"].get("categories", [])
            print(f"Name: {name}, Categories: {category}")
    elif status == 404:
        print("City not found or invalid input")  # examples
    elif status == 500:
        print("Error fetching attractions. Please try again later.")  # examples
