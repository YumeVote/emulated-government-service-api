"""
This script does pre-defined data related operations
1. Create a database
2. Create the citizen data table
3. Add 2 to 5 entires in to the database
4. Generate a hash of all the public keys and audit it onto the blockchain
"""

from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import utils
from dotenv import load_dotenv

import sqlite3
import hashlib
import os
import requests
import base64

def generate_hash(first_name, last_name, national_id):
    return hashlib.sha256((first_name + last_name + national_id).encode()).hexdigest()

def sign_data(data, private_key):
    return base64.b64encode(private_key.sign(
        data.encode(),
        ec.ECDSA(hashes.SHA256())
    )).decode()

def create_citizen(first_name, last_name, national_id, conn, cursor):
    # Generate ec private key
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    # Derive the public key from the private key
    public_key = private_key.public_key()

    # Serialize the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    candidate_firstname = first_name
    candidate_lastname = last_name
    candidate_nationid = national_id
    candidate_hash = generate_hash(candidate_firstname, candidate_lastname, candidate_nationid)
    candidate_digitalidentitysignature = sign_data(candidate_hash, private_key)
    # Insert a new citizen into the table
    cursor.execute('''
        INSERT INTO Citizen (First_Name, Last_Name, National_ID, Hash, Private_Key, Public_Key, DigitalIdentitySignature)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (candidate_firstname, candidate_lastname, candidate_nationid, candidate_hash, private_pem.decode(), public_pem.decode(), candidate_digitalidentitysignature))

    conn.commit()

load_dotenv()

MASCHAIN_CLIENT_ID = os.getenv("MASCHAIN_CLIENT_ID")
MASCHAIN_CLIENT_SECRET = os.getenv("MASCHAIN_CLIENT_SECRET")
ORGANIZATION_WALLET_ADDRESS = os.getenv("ORGANIZATION_WALLET_ADDRESS")
GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS = os.getenv("GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS")

print("MASCHAIN_CLIENT_KEY: ", MASCHAIN_CLIENT_ID)
print("MASCHAIN_CLIENT_SECRET: ", MASCHAIN_CLIENT_SECRET)
print("ORGANIZATION_WALLET_ADDRESS: ", ORGANIZATION_WALLET_ADDRESS)
print("PUBLIC_KEY_AUDIT_SMART_CONTRACT: ", GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS)

if not os.path.exists('assets'):
    os.makedirs('assets')

conn = sqlite3.connect('assets/citizen.sql')
cursor = conn.cursor()

# Create the Citizen table
cursor.execute('''
    CREATE TABLE Citizen (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        First_Name TEXT,
        Last_Name TEXT,
        National_ID TEXT UNIQUE,
        Hash TEXT,
        Private_Key TEXT UNIQUE,
        Public_Key TEXT UNIQUE,
        DigitalIdentitySignature TEXT UNIQUE
    )
''')

create_citizen('John', 'Mak', '1234567890', conn, cursor)
create_citizen('Jane', 'Doe', '0987654321', conn, cursor)

conn.commit()

# Fetch all the public keys from the Citizen table
cursor.execute('SELECT Public_Key FROM Citizen')
public_keys = [public_keys_query_output[0] for public_keys_query_output in cursor.fetchall()]

# Generate a hash of the public key list
public_keys_hash = hashlib.sha256(''.join(public_keys).encode()).hexdigest()
print(public_keys_hash)

#audit the hash onto the blockchain
# build the header
headers = {
    "client_id": MASCHAIN_CLIENT_ID,
    "client_secret": MASCHAIN_CLIENT_SECRET,
    "content-type": "application/json"
}

# Make the API request with the JSON string
response = requests.post(
    headers=headers,
    url="https://service-testnet.maschain.com/api/audit/audit",
    params={
        "wallet_address": ORGANIZATION_WALLET_ADDRESS,
        "contract_address": GOVERNMENT_AUDIT_SMART_CONTRACT_ADDRESS,
        "metadata": public_keys_hash,
        "callback_url": "http://gmail.com"
    }
)

transactionHash = response.json()['result']['transactionHash']
print("The transaction hash is: " + transactionHash)

# Write the transaction hash to a file
with open('assets/transactionhash.txt', 'w') as file:
    file.write(transactionHash)

conn.close()