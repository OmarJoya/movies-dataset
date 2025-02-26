import altair as alt
import pandas as pd
import streamlit as st
import hashlib

import datetime
# Import the JWT library and its exceptions.
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError

SECRET_KEY = "test"

# Function to derive the key (to match the hashing done in .NET)
def derive_key(secret_key):
    return hashlib.sha256(secret_key.encode()).digest()

def generateToken():
    # List of location codes you want in the payload
    location_codes = ["ALDBAT", "ALDCTV", "DGLEEB"]

    # Create payload with location codes
    payload = {
        "locations": location_codes,  # List of location codes
        "iat": datetime.datetime.utcnow(),  # Issued at (current time)
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Expiration time (30 seconds)
    }
    derived_key = derive_key(SECRET_KEY)
    token = jwt.encode(payload, derived_key, algorithm="HS256")
    st.write("JWT generado:", token)

# generateToken()

def is_token_valid(token):
    try:
         # Derive the same 32-byte key used in .NET
        derived_key = derive_key(SECRET_KEY)

        # Decode the JWT and verify its signature
        decoded_token = jwt.decode(token, derived_key, algorithms=["HS256"])
        st.write(f"Payload: {decoded_token}")
        
        # If we successfully decode it, the token is valid
        return True

    except ExpiredSignatureError:
        # Token has expired
        print("Token has expired.")
        return False

    except DecodeError:
        # Token is invalid (malformed or incorrect signature)
        print("Token is invalid.")
        return False

query_params = st.query_params

token = query_params.get("token", [None])
token_valid = False
if token:
    token_valid = is_token_valid(token)

if not token_valid:
    st.write("Token invalid")