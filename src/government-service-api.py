"""
This script exposes API as an emulated service provided by the government
1. Get the public keys of all the citizens
2. Get the latest transaction hash
3. Get the hash of the public keys

To verify the government is not cheating, the third-party auditors can use maschain blockchain explorer to audit the transaction hash to obtain the latest transaction hash
"""

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

import sqlite3
import os
import requests

load_dotenv()

app = FastAPI()

MASCHAIN_CLIENT_ID = os.getenv("MASCHAIN_CLIENT_ID")
MASCHAIN_CLIENT_SECRET = os.getenv("MASCHAIN_CLIENT_SECRET")
ORGANIZATION_WALLET_ADDRESS = os.getenv("ORGANIZATION_WALLET_ADDRESS")
GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS = os.getenv("GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS")

with open('assets/transactionhash.txt', 'r') as file:
    transaction_hash = file.read()

# build the header
headers = {
    "client_id": MASCHAIN_CLIENT_ID,
    "client_secret": MASCHAIN_CLIENT_SECRET,
    "content-type": "application/json"
}

@app.get("/")
def read_root():
    return "Hello World from Government Service API"

@app.get("/keys")
def get_keys():
    """
        returns all the public keys of the citizens without revealing the critical details
    """
    conn = sqlite3.connect('assets/citizen.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT Public_Key FROM Citizen')
    public_keys = [public_keys_query_output[0] for public_keys_query_output in cursor.fetchall()]
    return public_keys

@app.post("/verify")
def verify_citizen(digitalIdentitySignature: str):
    """
        digitalIdentitySignature that is going to be generated by the voting machine
        returns the citizen's public key if the digital identity signature is valid
    """
    conn = sqlite3.connect('assets/citizen.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Citizen WHERE DigitalIdentitySignature = ?', (digitalIdentitySignature,))
    record_exists = cursor.fetchone()[0]
    
    if record_exists:
        return "Citizen exists"
    else:
        raise HTTPException(status_code=404, detail="Citizen does not exist")

@app.get("/transactionHash")
def get_transaction_hash():
    """
        returns the latest transaction hash the government say it is
    """
    return transaction_hash

@app.get("/publicKeyHash")
def get_public_key_hash():
    """
        returns the hash of the public keys
    """
    # Make the API request with the JSON string
    response = requests.get(
        headers=headers,
        url="https://service-testnet.maschain.com/api/audit/audit/"+transaction_hash,
    )
    return response.json()["result"]["metadatahash"]