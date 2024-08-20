# mpesa_utils.py

import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime

# Function to get MPESA access token
def get_mpesa_access_token(consumer_key, consumer_secret):
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token

# Function to initiate MPESA payment
def lipa_na_mpesa_online(mpesa_number, amount, account_reference, consumer_key, consumer_secret, shortcode, passkey, callback_url):
    access_token = get_mpesa_access_token(consumer_key, consumer_secret)
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {'Authorization': f'Bearer {access_token}'}

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode('utf-8')

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": mpesa_number,
        "PartyB": shortcode,
        "PhoneNumber": mpesa_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": "Payment for Internet Package"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

