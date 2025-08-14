import requests
import json
import random
from faker import Faker
import re
import time


# Load test cards
with open("config/cards.json", "r") as f:
    CARDS = json.load(f)

fake = Faker()

# --- API Endpoints ---
TOKENIZATION_URL = "https://pay.sandbox.datatrans.com/upp/payment/SecureFields/paymentField"
CHECKOUT_URL = "https://checkout-api-dev.payintelli.com/api/v1/checkout/create"
#CHECKOUT_URL = "https://checkout-api-dev.payintelli.com/api/v1/checkout/create"
PAYMENT_URL = "https://api-dev.payintelli.com/api/v1/payments/create"
#PAYMENT_URL = "http://localhost:8082/api/v1/payments/create"
def tokenize_card(card):
    """Call Datatrans SecureFields API to tokenize card details"""
    payload = {
        "mode": "TOKENIZE",
        "formId": "250729103005965673",
        "cardNumber": card["number"],
        "cvv": card["cvv"],
        "paymentMethod": "VIS",
        "merchantId": "1110020135",
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

    response = requests.post(TOKENIZATION_URL, data=payload)
    response.raise_for_status()
    return response.json()

def create_checkout(amount, currency):
    

    # Generate and clean phone number
    raw_phone = re.sub(r'\D', '', fake.phone_number())

    # Remove leading country codes like '001' or '00'
    if raw_phone.startswith("00"):
        raw_phone = raw_phone[2:]
    elif raw_phone.startswith("1") and len(raw_phone) > 10:
        raw_phone = raw_phone[1:]

    # Ensure final phone number is 10–12 digits max
    phone = raw_phone[:12] if len(raw_phone) > 12 else raw_phone
    """Create checkout with random user data"""
    payload = {
        "clientId": "client_002",
        "transaction": {
        "amount": amount,
        "currency": currency
        },
        "clientOrderDetails": {
            "clientOrderId": fake.uuid4(),
            "description": "Subscription payment for SamagyaanDataSolutions",
            "clientId": "client_001"
        },
        "userDetails": {
            "clientUserId":fake.uuid4(),
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "email": fake.email(),
            "phone": phone,
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "country": fake.country_code(),
            "postalCode": fake.postcode(),
        },
        "notification": {
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
            "webhookUrl": "https://example.com/webhook"
        }
    }

    print(payload)
    response = requests.post(CHECKOUT_URL, json=payload)
    if response.status_code != 200:
        print("Checkout API error:", response.status_code, response.text)
    response.raise_for_status()

    return response.json()

def create_payment(token_data, checkout_data, card, amount, currency,card_holdername):
    """Create payment using tokenized data and checkout response"""
    
    payload = {
        "checkoutId": checkout_data.get("checkoutId", "missing_checkoutId"),
        "cardData": {
            "cardHolderName": card_holdername,
            "expiryMonth": card["month"],
            "expiryYear": card["year"],
            "encryptedCvv": token_data.get("cvv", "dummyCvv"),
            "encryptedCreditCardNumber": token_data.get("creditCard", "dummyNumber"),
            "pciProxyTransactionId": token_data.get("transactionId", "dummyTransaction")
        },
       "transaction": {
            "amount": amount,
            "currency": currency
        },
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
        "additionalData": {
            "additionalProp1": "string"
        }
    }
    
    response = requests.post(PAYMENT_URL, json=payload)
    response.raise_for_status()
    return response.json()

def run_test(iterations=1):
    for i in range(iterations):
        print(f"\n--- Test Run {i+1} ---")
        card = CARDS[i] 
        print("Using card:", card["number"])
        
        # Step 1: Tokenize
        token_data = tokenize_card(card)
        print("Tokenization Response:", token_data)

        amount = round(random.uniform(3000, 4000))
        currency = random.choice(["EUR", "EUR"])
        
        # Step 2: Checkout
        checkout_data = create_checkout(amount, currency)
        print("Checkout Response:", checkout_data)
        
        #statuses = ["refund failed", "ChargebackReversed", "SecondChargeback","Chargeback","refund failed", "ChargebackReversed", "SecondChargeback","refund failed"]
        cardHolderName = f"{fake.first_name()} {fake.last_name()}";
        # Step 3: Payment
        payment_data = create_payment(token_data, checkout_data['data'], card, amount, currency,cardHolderName)
        print("Payment Response:", payment_data)
        time.sleep(5)
if __name__ == "__main__":
    run_test(iterations=1)
