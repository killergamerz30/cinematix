import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Cinematix | Live Box Office",
    page_icon="🎬",
    layout="wide"
)

# ==================================================
# DARK CINEMATIC STYLE
# ==================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #090A0F 0%,
            #151821 100%
        );
    }

    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #9CA3AF;
        font-size: 18px;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# POSTER FUNCTION
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
# LIVE BOX OFFICE SCRAPER
# ==================================================

@st.cache_data(ttl=14400)
def get_box_office_data():

    url = "https://www.boxofficemojo.com/year/world/2026/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
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

        if table is None:
            return pd.DataFrame(
                columns=[
                    "Rank",
                    "Title",
                    "Gross"
                ]
            )

        movies = []

        rows = table.find_all("tr")[1:101]

        for row in rows:

            cells = row.find_all("td")

            if len(cells) < 3:
                continue

            rank_text = cells[0].get_text(
                strip=True
            )

            title = cells[1].get_text(
                strip=True
            )

            gross = cells[2].get_text(
                strip=True
            )

            if not title:
                continue

            if rank_text.isdigit():
                rank = int(rank_text)
            else:
                rank = len(movies) + 1

            movies.append(
                {
                    "Rank": rank,
                    "Title": title,
                    "Gross": gross
                }
            )

        return pd.DataFrame(movies)

    except Exception as error:

        st.error(
            "Unable to load live box-office data."
        )

        st.caption(
            f"Error: {error}"
        )

        return pd.DataFrame(
            columns=[
                "Rank",
                "Title",
                "Gross"
            ]
        )


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

st.markdown(
    '<div class="main-title">🎬 CINEMATIX HUNDRED</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Live Global Box Office Matrix • '
    'Top 100 Performance Metrics'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR SEARCH
# ==================================================

st.sidebar.title("🛠️ Navigation Filter")

search = st.sidebar.text_input(
    "🔍 Quick Title Lookup"
)


# ==================================================
# SEARCH FILTER
# ==================================================

if search:

    df_movies = df_movies[
        df_movies["Title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]


# ==================================================
# MOVIE DISPLAY
# ==================================================

if df_movies.empty:

    st.warning(
        "No movie data is currently available."
    )

else:

    st.markdown(
        f"### 📊 Active Database Inventory "
        f"({len(df_movies)} Movies Displayed)"
    )

    # ------------------------------------------------
    # TOP MOVIE
    # ------------------------------------------------

    top_movie = df_movies.iloc[0]

    st.success(
        f"🔥 GLOBAL LEADERBOARD KING\n\n"
        f"**{top_movie['Title']}**\n\n"
        f"{top_movie['Gross']} Worldwide Gross"
    )

    st.divider()

    # ------------------------------------------------
    # FOUR COLUMN MOVIE GRID
    # ------------------------------------------------

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
                st.markdown(
                    f"**RANK #{movie['Rank']}**"
                )

                # Title
                st.markdown(
                    f"### {movie['Title']}"
                )

                # Gross
                st.caption(
                    "BOX OFFICE TOTAL"
                )

                st.markdown(
                    f"**{movie['Gross']}**"
                )

                st.divider()
