# simulator.py
import os
import requests
import json
import random
from faker import Faker
import re
import time
import pandas as pd

# --- Config via ENV (with sensible defaults) ---
CSV_PATH = os.getenv("CSV_PATH", "data/Client002.csv")
CARDS_PATH = os.getenv("CARDS_PATH", "config/cards.json")
TOKENIZATION_URL = os.getenv("TOKENIZATION_URL", "https://pay.sandbox.datatrans.com/upp/payment/SecureFields/paymentField")
CHECKOUT_URL     = os.getenv("CHECKOUT_URL",     "https://checkout-api-dev.payintelli.com/api/v1/checkout/create")
PAYMENT_URL      = os.getenv("PAYMENT_URL",      "https://api-dev.payintelli.com/api/v1/payments/create")
CLIENT_ID        = os.getenv("CLIENT_ID", "client_002")
FORM_ID          = os.getenv("FORM_ID", "250729103005965673")
MERCHANT_ID      = os.getenv("MERCHANT_ID", "1110020135")

fake = Faker()

# Load test cards
with open(CARDS_PATH, "r") as f:
    CARDS = json.load(f)

# Lazy-loaded CSV dataframe placeholder
df = None

def tokenize_card(card):
    """Call Datatrans SecureFields API to tokenize card details"""
    payload = {
        "mode": "TOKENIZE",
        "formId": FORM_ID,
        "cardNumber": card["number"],
        "cvv": card["cvv"],
        "paymentMethod": "VIS",
        "merchantId": MERCHANT_ID,
        "expy": card["year"],
        "expm": card["month"],
        "browserUserAgent": "Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64)",
        "browserJavaEnabled": "false",
        "browserLanguage": "en-US",
        "browserColorDepth": "24",
        "browserScreenHeight": "1080",
        "browserScreenWidth": "1920",
        "browserTZ": "-330"
    }
    r = requests.post(TOKENIZATION_URL, data=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def _clean_phone(num: str) -> str:
    raw = re.sub(r'\D', '', num)
    if raw.startswith("00"):
        raw = raw[2:]
    elif raw.startswith("1") and len(raw) > 10:
        raw = raw[1:]
    return raw[:12]

def create_checkout(amount, currency):
    global df
    if df is None:
        print(f"Loading CSV from {CSV_PATH} ...", flush=True)
        try:
            import pandas as pd  # local import to allow deferred failure & smaller startup cost
            df = pd.read_csv(CSV_PATH, low_memory=False)
            print(f"Loaded {len(df)} rows from CSV", flush=True)
        except Exception as e:
            print(f"Failed to load CSV: {e}", flush=True)
            raise

    row = df.sample(1).iloc[0]

    first_name = row.get('First_Name')
    last_name = row.get('Last_Name')
    email = row.get('Email_Address')
    address = row.get('Address_line1')
    city = row.get('City')
    state = row.get('State')
    postal_code = row.get('Postal_Code')

    first_name = first_name if pd.notna(first_name) and str(first_name).strip() else fake.first_name()
    last_name  = last_name  if pd.notna(last_name)  and str(last_name).strip()  else fake.last_name()
    email      = email      if pd.notna(email)      and str(email).strip()      else fake.email()
    address    = address    if pd.notna(address)    and str(address).strip()    else fake.street_address()
    city       = city       if pd.notna(city)       and str(city).strip()       else fake.city()
    state      = state      if pd.notna(state)      and str(state).strip()      else fake.state()
    postal_code = str(postal_code) if pd.notna(postal_code) else fake.postcode()
    phone = _clean_phone(fake.phone_number())
    country = fake.country_code()

    payload = {
        "clientId": CLIENT_ID,
        "transaction": {"amount": amount, "currency": currency},
        "clientOrderDetails": {
            "clientOrderId": fake.uuid4(),
            "description": "Subscription payment for SamagyaanDataSolutions",
            "clientId": CLIENT_ID
        },
        "userDetails": {
            "clientUserId": fake.uuid4(),
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "country": country,
            "postalCode": postal_code
        },
        "notification": {
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
            "webhookUrl": "https://example.com/webhook"
        }
    }

    print(payload, flush=True)

    r = requests.post(CHECKOUT_URL, json=payload, timeout=60)
    if r.status_code != 200:
        print("Checkout API error:", r.status_code, r.text, flush=True)
    r.raise_for_status()
    return r.json()

def create_payment(token_data, checkout_data, card, amount, currency):
    payload = {
        "checkoutId": checkout_data.get("checkoutId", "missing_checkoutId"),
        "cardData": {
            "cardHolderName": f"{fake.first_name()} {fake.last_name()}",
            "expiryMonth": card["month"],
            "expiryYear": card["year"],
            "encryptedCvv": token_data.get("cvv", "dummyCvv"),
            "encryptedCreditCardNumber": token_data.get("creditCard", "dummyNumber"),
            "pciProxyTransactionId": token_data.get("transactionId", "dummyTransaction")
        },
        "transaction": {"amount": amount, "currency": currency},
        "browserDetails": {
            "userAgent": "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9) Gecko/2008052912 Firefox/3.0",
            "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "javaEnabled": True,
            "colorDepth": 24,
            "screenHeight": 2000,
            "screenWidth": 3000,
            "timeZoneOffset": 5,
            "language": "en"
        },
        "additionalData": {"additionalProp1": "string"}
    }
    r = requests.post(PAYMENT_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def run_test(iterations=1):
    for i in range(iterations):
        print(f"\n--- Test Run {i+1} ---", flush=True)
        card = random.choice(CARDS)
        print("Using card:", card["number"], flush=True)

        token_data = tokenize_card(card)
        print("Tokenization Response:", token_data, flush=True)

        amount = round(random.uniform(1, 4000))
        currency = random.choice(["EUR", "GBP"])

        checkout_data = create_checkout(amount, currency)
        print("Checkout Response:", checkout_data, flush=True)

        # If API returns {"data": {...}} shape, keep this:
        payload_for_payment = checkout_data.get('data', checkout_data)

        payment_data = create_payment(token_data, payload_for_payment, card, amount, currency)
        print("Payment Response:", payment_data, flush=True)

        time.sleep(20)
