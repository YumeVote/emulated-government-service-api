"""
This script does pre-defined data related operations
1. Create a database
2. Create the citizen data table
3. Add 2 to 5 entires in to the database
4. Generate a hash of all the public keys and audit it onto the blockchain
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import utils
from dotenv import load_dotenv

import sqlite3
import hashlib
import os
import requests

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
        Private_Key TEXT,
        Public_Key TEXT
    )
''')


# Generate RSA private key
private_key_1 = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Derive the public key from the private key
public_key_1 = private_key_1.public_key()

# Serialize the private key
private_pem_1 = private_key_1.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize the public key
public_pem_1 = public_key_1.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Insert a new citizen into the table
cursor.execute('''
    INSERT INTO Citizen (First_Name, Last_Name, National_ID, Hash, Private_Key, Public_Key)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('John', 'Doe', '1234567890', hashlib.sha256(('John' + 'Doe' + '1234567890').encode()).hexdigest(),private_pem_1.decode(), public_pem_1.decode()))

# Generate RSA private key
private_key_2 = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Derive the public key from the private key
public_key_2 = private_key_2.public_key()

# Serialize the private key
private_pem_2 = private_key_2.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize the public key
public_pem_2 = public_key_2.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Insert a new citizen into the table
cursor.execute('''
    INSERT INTO Citizen (First_Name, Last_Name, National_ID, Hash, Private_Key, Public_Key)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('James', 'Mak', '43124abcd', hashlib.sha256(('James' + 'Mak' + '43124abcd').encode()).hexdigest(), private_pem_2.decode(), public_pem_2.decode()))

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