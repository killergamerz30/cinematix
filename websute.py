import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Cinematix | Live Box Office",
    page_icon="🎬",
    layout="wide"
)

# ==================================================
# PAGE DESIGN
# ==================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #07090D,
            #111827,
            #07090D
        );
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# POSTERS
# ==================================================

def get_movie_poster(number):

    posters = [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
        "https://images.unsplash.com/photo-1485846234645-a62644f84728",
        "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c",
        "https://images.unsplash.com/photo-1440404653325-ab127d49abc1",
        "https://images.unsplash.com/photo-1485095329183-d0797cdc5676"
    ]

    return posters[number % len(posters)]


# ==================================================
# LIVE BOX OFFICE
# ==================================================

@st.cache_data(ttl=14400)
def get_box_office_data():

    url = "https://www.boxofficemojo.com/year/world/2026/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        table = soup.find(
            "table",
            class_="mojo-body-table"
        )

        movies = []

        if table:

            rows = table.find_all("tr")[1:101]

            for row in rows:

                cells = row.find_all("td")

                if len(cells) >= 3:

                    rank = cells[0].get_text(
                        strip=True
                    )

                    title = cells[1].get_text(
                        strip=True
                    )

                    gross = cells[2].get_text(
                        strip=True
                    )

                    if title:

                        movies.append(
                            {
                                "Rank": int(rank)
                                if rank.isdigit()
                                else len(movies) + 1,

                                "Title": title,

                                "Gross": gross
                            }
                        )

        return pd.DataFrame(movies)

    except Exception as error:

        st.error(
            "Unable to load box-office data."
        )

        st.caption(str(error))

        return pd.DataFrame()


# ==================================================
# LOAD DATA
# ==================================================

with st.spinner(
    "Loading live worldwide box-office data..."
):

    df_movies = get_box_office_data()


# ==================================================
# HEADER
# ==================================================

st.title("🎬 CINEMATIX HUNDRED")

st.subheader(
    "Live Global Box Office Matrix • "
    "Top 100 Performance Metrics"
)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header(
    "🛠️ Navigation Filter"
)

search = st.sidebar.text_input(
    "🔍 Quick Title Lookup"
)


# ==================================================
# SEARCH
# ==================================================

if search and not df_movies.empty:

    df_movies = df_movies[
        df_movies["Title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]


# ==================================================
# MOVIE RESULTS
# ==================================================

if df_movies.empty:

    st.warning(
        "No movie data is currently available."
    )

else:

    st.write(
        f"### 📊 Active Database Inventory "
        f"({len(df_movies)} Movies Displayed)"
    )

    # ==================================================
    # LEADER
    # ==================================================

    top_movie = df_movies.iloc[0]

    st.success(
        f"🔥 GLOBAL LEADERBOARD KING\n\n"
        f"**{top_movie['Title']}**\n\n"
        f"{top_movie['Gross']} Worldwide Gross"
    )

    st.divider()

    # ==================================================
    # MOVIE GRID
    # ==================================================

    for start in range(
        0,
        len(df_movies),
        4
    ):

        columns = st.columns(4)

        for position in range(4):

            index = start + position

            if index >= len(df_movies):
                break

            movie = df_movies.iloc[index]

            with columns[position]:

                # Poster
                st.image(
                    get_movie_poster(index),
                    use_container_width=True
                )

                # Rank
                st.caption(
                    f"RANK #{movie['Rank']}"
                )

                # Movie name
                st.markdown(
                    f"**{movie['Title']}**"
                )

                # Box office label
                st.caption(
                    "BOX OFFICE TOTAL"
                )

                # Box office amount
                st.markdown(
                    f"### {movie['Gross']}"
                )

                st.divider()
