# Emulated Government Service API

Author : Victor Mak (Htet Aung Hlaing)

# Target Requirements

1. An emulated government database with citizen data (does not have to be real), a hash of aforementioned metadata, private key and public key
2. An emulated government blockchain with Maschain with Audit Service enabled that have one Auditing Smart Contract stores the hash of the public key exposed
3. An emulated government api service that exposes all the public key data, a hash of those public keys (to ensure the government does not went wrong internally) is kept on the blockchain and txID is made public for everybody to see and recheck themselves as necessary

# Solutions

1. Using the ```data-setup.py``` an emulated database will be setup as per the requirement
2. Also in the ```data-setup.py``` the hash of all the public keys is stored on a blockchain audit smart contract for auditting purposes
3. ```government-service-api.py``` exposes three apis to the public
    1. Get the public keys of all the citizens
    2. Get the latest transaction hash
    3. Get the hash of the public keys

# How To Run

To set things up easily, I have quickly created a Makefile.

1. ```make install```
    - Install the necessary python packages
2. ```make setup```
    - clean the database and set up a new database
3. ```make```
    - install the packages
    - starts the api server
