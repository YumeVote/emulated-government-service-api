from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello World from Government Service API"

@app.get("/citizen-public-keys")
def read_citizen_public_keys():
    return "Getting Citizen Public Keys"