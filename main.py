from phonenumber import register_number, unregister_number
from blabla import send_sms



register_number(34823745845)
send_sms(text, phone_number)

# swagger: http://hackathons.masterschool.com:3030/api-docs/#/
# teamname: Attraction

# add team

# register a phone number

# unregister a phone number

# read the messages

# send a message


# fetch attraction places from api

# user init:
# - location
# - type of attraction

# persistent storage (keep track of app and user status and received messages

# parce response, create sms text (<= 160 symbols or <= 70 for umlauts)

""" sms code words:
SUBSCRIBE $phone_number
LOCATION $location
TYPE $attractin_type 
"""


""" main while loop:
- check for messages every 10s
- if there any new messages check the user from storage

1. ask for a location
2. ask for a type of attraction
3. send sms
"""

