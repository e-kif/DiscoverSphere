import requests

URL = "http://hackathons.masterschool.com:3030"
team_name = "Attraction"


def register_number(number) -> int:
    """
    Registers a phone number to the specified team.
    """
    url = f"{URL}/team/registerNumber"
    print(url)
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "teamName": team_name}
    response = requests.post(url, json=body)

    print(f'{response.text=}')
    print(f'{response=}')
    return response.status_code


def unregister_number(number) -> int:
    """
    Unregisters a phone number from the specified team.
    """
    url = f"{URL}/team/unregisterNumber"
    print(url)
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "teamName": team_name}
    response = requests.post(url, json=body)

    print(f'{response.text=}')
    print(f'{response=}')
    return response.status_code


def read_messages(team_name) -> list:
    """
    This function retrieves all messages for the given team.
    """
    url = f"{URL}/team/getMessages/{team_name}"
    print(url)
    response = requests.get(url)

    print(f'{response.text=}')
    print(f'{response=}')

    if response.status_code == 200:
        return response.json()
    else:
        print("Error downloading message.")
        return []


def send_message(number: int, text: str) -> int:
    """
    The function sends an SMS message to the specified number.
    """
    url = f"{URL}/sms/send"
    print(url)
    headers = {"Content-type": "application/json"}
    body = {"phoneNumber": number, "message": text}
    response = requests.post(url, json=body)

    print(f'{response.text=}')
    print(f'{response=}')

    return response.status_code


code = register_number(123456679)
print(code)
code = unregister_number(123456679)
print(code)

messages = read_messages(team_name)
print(f"Messages: {messages}")

response_code = send_message(1234567890, "Hello, this is a test message!")
print(f"Response code: (send_message): {response_code}")

