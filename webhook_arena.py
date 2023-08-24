import requests
import datetime
from urllib.parse import urljoin

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import os

# Define your variables
_format = "json"
BASE_URL = os.getenv('BASE_URL')
SPORT_EVENT_ID = os.getenv('SPORT_EVENT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_KEY = os.getenv('API_KEY')
CRED_PATH = os.getenv('CRED_PATH')
FIREBASE_URL = os.getenv('FIREBASE_URL')

api_token = None
expired_token = None

cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_URL
})


def request_token():
    global api_token
    global expired_token
    # If api_token is not valid or is about to expire, request a new one
    if api_token is None or datetime.datetime.now() >= expired_token:
        print("Requesting a new token")
        auth_url = urljoin(BASE_URL, "/oauth/v2/token")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            "grant_type": "https://arena.uww.io/grants/api_key",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "api_key": API_KEY
        }
        response = requests.post(auth_url, headers=headers, data=data)
        if response.status_code == 200:
            response_json = response.json()
            api_token = response_json['access_token']
            expired_token = datetime.datetime.now() + datetime.timedelta(seconds=response_json['expires_in'])

def get_fight_data():
    global api_token

    fight_url = urljoin(BASE_URL, f"/api/{_format}/fight/{SPORT_EVENT_ID}")
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    response = requests.get(fight_url, headers=headers)

    # Process the response
    if response.status_code == 200:
        fight_data = response.json()

        # Get a database reference to our posts
        ref = db.reference('fights')
        
        sorted_fights = sorted(fight_data['fights'], key=lambda fight: int(fight['fightNumber']))
        ref.set(sorted_fights)



for i in range(2):
    request_token()

    start_time = time.time()

    get_fight_data()

    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    time.sleep(60)
