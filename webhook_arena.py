import requests
import datetime
from urllib.parse import urljoin
import firebase_admin
from firebase_admin import credentials, auth, db
from flask import Flask, request

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
ADMIN_UID = os.getenv('ADMIN_UID')

api_token = None
expired_token = None

# Initialize Firebase app
cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_URL
})

# Create a custom token with admin claims
def create_custom_token():
    additional_claims = {
        "admin": True,
    }   
    return auth.create_custom_token(ADMIN_UID, additional_claims)

# Request API Token from external service
def request_token():
    global api_token
    global expired_token
    if api_token is None or datetime.datetime.now() >= expired_token:
        # print("Requesting a new token")
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
            # print(api_token)
            expired_token = datetime.datetime.now() + datetime.timedelta(seconds=response_json['expires_in'])

def get_fights():
    fight_url = urljoin(BASE_URL, f"/api/{_format}/fight/{SPORT_EVENT_ID}")
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    response = requests.get(fight_url, headers=headers)

    if response.status_code == 200:
        fights_data = response.json()

        ref = db.reference('fights')
        
        sorted_fights = sorted(fights_data['fights'], key=lambda fight: int(fight['fightNumber']))
        ref.set(sorted_fights)

        ranking = {}
        for fight in sorted_fights:
            if fight.get('weightCategoryCompleted', False):
                weight_category_id = fight.get('sportEventWeightCategoryId')
                weight_category_name = fight.get('weightCategoryAlternateName')
                if weight_category_id and weight_category_name not in ranking:
                    rank = get_ranking(weight_category_id)
                    ranking[weight_category_name] = rank
        
        refRanking = db.reference('ranking')
        refRanking.set(ranking)

def get_fight(id):
    fight_url = urljoin(BASE_URL, f"/api/{_format}/fight/get/{id}")
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    response = requests.get(fight_url, headers=headers)

    if response.status_code == 200:
        fight_data = response.json()
        fight = fight_data['fight']
        fight_number = fight['fightNumber'] - 1

        ref = db.reference(f'fights/{fight_number}')
        ref.set(fight)

        if fight.get('weightCategoryCompleted', False):
            weight_category_id = fight.get('sportEventWeightCategoryId')
            weight_category_name = fight.get('weightCategoryAlternateName')
            rank = get_ranking(weight_category_id)
            
            refRanking = db.reference(f'ranking/{weight_category_name}')
            refRanking.set(rank)

def get_ranking(id):
    ranking_url = urljoin(BASE_URL, f"/api/{_format}/weight-category/get/{id}/ranking")
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    response = requests.get(ranking_url, headers=headers)

    if response.status_code == 200:
        response_ranking = response.json()
        if response_ranking.get('isCompleted'):
            ranking_data = response_ranking['ranking']
            ranking_list = list(ranking_data.values())

            sorted_rankings = sorted(ranking_list, key=lambda x: x['fighter']['rank'])

            return sorted_rankings

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello, this is ARENA Webhook', 200


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)
    
    request_token()
    get_fight(data['id'])
    return 'Success', 200


if __name__ == '__main__':
    request_token()
    get_fights()
    app.run(port=5000)