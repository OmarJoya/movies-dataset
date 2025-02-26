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
    
    # Generar el JWT
    token = jwt.encode(payload, derived_key, algorithm="HS256")
    # Mostrar el JWT
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
else:

    # Load the data from a CSV. We're caching this so it doesn't reload every time the app
    # reruns (e.g. if the user interacts with the widgets).
    @st.cache_data
    def load_data():
        df = pd.read_csv("data/movies_genres_summary.csv")
        return df


    df = load_data()

    # Show a multiselect widget with the genres using `st.multiselect`.
    genres = st.multiselect(
        "Genres",
        df.genre.unique(),
        ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
    )

    # Show a slider widget with the years using `st.slider`.
    years = st.slider("Years", 1986, 2006, (2000, 2016))

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
    df_reshaped = df_filtered.pivot_table(
        index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
    )
    df_reshaped = df_reshaped.sort_values(by="year", ascending=False)


    # Display the data as a table using `st.dataframe`.
    st.dataframe(
        df_reshaped,
        use_container_width=True,
        column_config={"year": st.column_config.TextColumn("Year")},
    )

    # Display the data as an Altair chart using `st.altair_chart`.
    df_chart = pd.melt(
        df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
    )
    chart = (
        alt.Chart(df_chart)
        .mark_line()
        .encode(
            x=alt.X("year:N", title="Year"),
            y=alt.Y("gross:Q", title="Gross earnings ($)"),
            color="genre:N",
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)
