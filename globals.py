import os
from dotenv import load_dotenv
load_dotenv()

MONGO_HOST = "localhost"
DB = "reward-cycle"
PORT = 27017


embeddings = []


def add_to_embeddings(username, encoding):
    interm = {
        "name": username,
        "encoding": encoding
    }
    embeddings.append(interm)

