import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Cinematix | Live Box Office Matrix",
    page_icon="🎬",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #090A0F 0%, #151821 100%);
    color: #E2E8F0;
}

.movie-meta-block {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 0 0 12px 12px;
    padding: 15px;
    margin-bottom: 25px;
}

.movie-rank {
    font-size: 0.85rem;
    font-weight: 700;
    color: #00F2FE;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 4px;
}

.movie-name {
    font-size: 1.15rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 10px;
    line-height: 1.3;
    min-height: 48px;
}

.metric-label {
    font-size: 0.75rem;
    color: #A0AEC0;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.metric-value {
    font-size: 1.2rem;
    font-weight: 700;
    color: #00E676;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# MOVIE POSTER
# --------------------------------------------------

def get_movie_poster(rank_num):
    img_pool = [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
        "https://images.unsplash.com/photo-1485846234645-a62644f84728",
        "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c",
        "https://images.unsplash.com/photo-1440404653325-ab127d49abc1",
        "https://images.unsplash.com/photo-1485095329183-d0797cdc5676"
    ]

    return img_pool[rank_num % len(img_pool)]

# --------------------------------------------------
# BOX OFFICE DATA
# --------------------------------------------------

@st.cache_data(ttl=14400)
def scrape_worldwide_box_office_data():

    url = "https://www.boxofficemojo.com/year/world/2026/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        movie_records = []

        table = soup.find(
            "table",
            class_="mojo-body-table"
        )

        if table:

            rows = table.find_all("tr")[1:101]

            for row in rows:

                cols = row.find_all("td")

                if len(cols) >= 3:

                    rank = cols[0].text.strip()
                    title = cols[1].text.strip()
                    gross = cols[2].text.strip()

                    if title and gross:

                        movie_records.append({
                            "Rank": int(rank)
                            if rank.isdigit()
                            else len(movie_records) + 1,

                            "Title": title,

                            "Gross": gross
                        })

        if len(movie_records) > 15:

            return pd.DataFrame(movie_records)

        return pd.DataFrame(
            columns=["Rank", "Title", "Gross"]
        )

    except Exception:

        return pd.DataFrame(
            columns=["Rank", "Title", "Gross"]
        )

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with st.spinner("Loading worldwide box-office data..."):

    df_movies = scrape_worldwide_box_office_data()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    "# 🎬 CINEMATIX HUNDRED"
)

st.markdown(
    "### Live Global Box Office Matrix • Top 100 Performance Metrics"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown(
    "### 🛠️ Navigation Filter"
)

search_filter = st.sidebar.text_input(
    "🔍 Quick Title Lookup:"
)

st.sidebar.markdown("---")

# --------------------------------------------------
# SEARCH
# --------------------------------------------------

if search_filter:

    df_movies = df_movies[
        df_movies["Title"].str.contains(
            search_filter,
            case=False,
            na=False
        )
    ]

# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

if df_movies.empty:

    st.warning(
        "Live box-office data is temporarily unavailable. Please try again later."
    )

else:

    st.markdown(
        f"### 📊 Active Database Inventory "
        f"({len(df_movies)} Movies Displayed)"
    )

    # --------------------------------------------------
    # TOP MOVIE
    # --------------------------------------------------

    top_movie = df_movies.iloc[0]

    st.success(
        f"🔥 GLOBAL LEADERBOARD KING\n\n"
        f"**{top_movie['Title']}**\n\n"
        f"{top_movie['Gross']} Worldwide Gross"
    )

    # --------------------------------------------------
    # MOVIE GRID
    # --------------------------------------------------

    for idx in range(
        0,
        len(df_movies),
        4
    ):

        cols = st.columns(4)

        for col_offset in range(4):

            item_idx = idx + col_offset

            if item_idx < len(df_movies):

                movie = df_movies.iloc[item_idx]

                with cols[col_offset]:

                    poster_url = get_movie_poster(
                        item_idx
                    )

                    st.image(
                        poster_url,
                        use_container_width=True
                    )

                    st.markdown(
                        f"""
                        <div class="movie-meta-block">

                            <div class="movie-rank">
                                Rank #{movie['Rank']}
                            </div>

                            <div class="movie-name">
                                {movie['Title']}
                            </div>

                            <div class="metric-label">
                                Box Office Total
                            </div>

                            <div class="metric-value">
                                {movie['Gross']}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )
