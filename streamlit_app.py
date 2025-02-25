import altair as alt
import pandas as pd
import streamlit as st


import datetime
# Import the JWT library and its exceptions.
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError

# Show the page title and description.
st.set_page_config(page_title="Movies dataset", page_icon="🎬")
st.title("🎬 Movies dataset")
st.write(
    """
    This app visualizes data from [The Movie Database (TMDB)](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).
    It shows which movie genre performed best at the box office over the years. Just 
    click on the widgets below to explore!
    """
)

SECRET_KEY = "test"

def generateToken():
    # List of location codes you want in the payload
    location_codes = ["LOC001", "LOC002", "LOC003"]

    # Create payload with location codes
    payload = {
        "locations": location_codes,  # List of location codes
        "iat": datetime.datetime.utcnow(),  # Issued at (current time)
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Expiration time (30 seconds)
    }
    # Generar el JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # Mostrar el JWT
    st.write("JWT generado:", token)

# generateToken()


def is_token_valid(token):
    try:
        # Decode the JWT and verify its signature
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
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
