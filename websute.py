import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
# 1. Professional Page Configurations & Theme Setup
st.set_page_config(page_title="Cinematix | Live Box Office Matrix", page_icon="🎬", layout="wide")

# Custom Dark Cinematic CSS Theme
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #090A0F 0%, #151821 100%);
        color: #E2E8F0;
    }
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 3.2rem;
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .movie-meta-block {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0px 0px 12px 12px;
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

# Helper function to generate clean image streams for all cards
def get_movie_poster(rank_num): 
    # Array of high-resolution film, cinema, and production placeholder assets
    img_pool = [
        "https://unsplash.com",
        "https://unsplash.com",
        "https://unsplash.com",
        "https://unsplash.com",
        "https://unsplash.com"
    ]
    return img_pool[rank_num % len(img_pool)]

# 2. Dynamic Real-Time Top 100 Scraper Component
@st.cache_data(ttl=14400)
def scrape_worldwide_box_office_data():
    url = "https://www.boxofficemojo.com/year/world/2026/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        movie_records = []
        table = soup.find('table', class_='mojo-body-table')
        
        if table:
            rows = table.find_all('tr')[1:101] # Extract the full Top 100 entries
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # FIX: Explicit index positions to eliminate compile time blocks
                    rank = cols[0].text.strip()
                    title = cols[1].text.strip()
                    gross = cols[2].text.strip()
                    
                    if title and gross:
                        movie_records.append({
                            "Rank": int(rank) if rank.isdigit() else len(movie_records) + 1,
                            "Title": title,
                            "Gross": gross
                        })
                        
        if len(movie_records) > 15:
            return pd.DataFrame(movie_records)
        raise ValueError()
        
except Exception:
    return pd.DataFrame(columns=["Rank", "Title", "Gross"])


# Fetch box-office data
with st.spinner("Loading box-office data..."):
    df_movies = scrape_worldwide_box_office_data()


# Dashboard Header
st.markdown("CINEMATIX HUNDRED")
st.markdown("Live Global Box Office Matrix • Top 100 Performance Metrics")


# Sidebar Search
st.sidebar.markdown("### 🛠️ Navigation Filter")
search_filter = st.sidebar.text_input("🔍 Quick Title Lookup:")
st.sidebar.markdown("---")


# Search
if search_filter:
    df_movies = df_movies[
        df_movies["Title"].str.contains(
            search_filter,
            case=False,
            na=False
        )
    ]


# Display Results
if df_movies.empty:
    st.warning("Live box-office data is temporarily unavailable.")
else:
    st.markdown(
        f"### 📊 Active Database Inventory ({len(df_movies)} Movies Displayed)"
    )

    top_movie = df_movies.iloc[0]

    st.markdown(
        f"""
        ### 🔥 GLOBAL LEADERBOARD KING

        **{top_movie['Title']}**

        {top_movie['Gross']} Worldwide Gross
        """
    )

    # Movie Grid
    for idx in range(0, len(df_movies), 4):
        cols = st.columns(4)

        for col_offset in range(4):
            item_idx = idx + col_offset

            if item_idx < len(df_movies):
                movie = df_movies.iloc[item_idx]

                with cols[col_offset]:
                    poster_url = get_movie_poster(item_idx)

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
