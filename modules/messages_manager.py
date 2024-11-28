import requests

URL = "http://hackathons.masterschool.com:3030"
team_name = "Attraction"


def register_number(number: int) -> tuple[int, str]:
    """
    Registers a phone number to the specified team.
    """
    url = f"{URL}/team/registerNumber"
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "teamName": team_name}
    response = requests.post(url, json=body)
    return response.status_code, response.text


def unregister_number(number: int) -> tuple[int, str]:
    """
    Unregisters a phone number from the specified team.
    """
    url = f"{URL}/team/unregisterNumber"
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "teamName": team_name}
    response = requests.post(url, json=body)
    return response.status_code, response.text


def read_messages(team_name: str) -> tuple[int, list | str]:
    """
    This function retrieves all messages for the given team.
    """
    url = f"{URL}/team/getMessages/{team_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.status_code, response.json()
    return response.status_code, "Error downloading message."


def send_message(number: int, text: str) -> tuple[int, str]:
    """
    The function sends an SMS message to the specified number.
    """
    url = f"{URL}/sms/send"
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "message": text}
    response = requests.post(url, json=body)
    return response.status_code, response.text


def run_tests():
    """
    Test the functionality of the implemented functions.
    """
    # Test register_number
    code, message = register_number(+4915735166871)
    print(f"Register Number -> Code: {code}, Message: {message}")

    # Test unregister_number
    code, message = unregister_number(+4915735166871)
    print(f"Unregister Number -> Code: {code}, Message: {message}")

    # Test read_messages
    code, messages = read_messages(team_name)
    print(f"Read Messages -> Code: {code}, Messages: {messages}")

    # Test send_message
    code, message = send_message(+4915735166871, "Hello, this is a test message!")
    print(f"Send Message -> Code: {code}, Message: {message}")


if __name__ == "__main__":
    run_tests()
