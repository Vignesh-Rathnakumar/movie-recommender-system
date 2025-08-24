import streamlit as st
import pickle
import pandas as pd
import requests

# Page config
st.set_page_config(page_title="Cine Mate", layout="wide")

# ------------------------
# Credit at top-right
# ------------------------
st.markdown(
    """
    <style>
    .top-right-credit {
        position: absolute;
        top: 15px;
        right: 25px;
        font-size: 12px;
        color: #cccccc;
        font-style: italic;
    }
    </style>
    <div class="top-right-credit">Project done by Vignesh</div>
    """,
    unsafe_allow_html=True
)

# OTT-style dark cinematic background
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
        url("https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }
    .stButton>button {
        background-color: #E50914;  /* OTT-red style button */
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-size: 18px;
        font-weight: bold;
    }
    .stSelectbox>div>div>div>select {
        background-color: rgba(255, 255, 255, 0.95);
        color: black;
        border-radius: 6px;
        padding: 5px;
    }
    .stHeader, .stSubheader {
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------
# Header line/banner
# ------------------------
st.markdown(
    """
    <div style="
        background-color: rgba(0,0,0,0.8);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #E50914;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    ">
        🎬 Welcome to <span style="color:#ffffff;">Cine Mate</span> 
    </div>
    """,
    unsafe_allow_html=True
)

# App title
st.title("🎬 Cine Mate")
st.subheader("Your personal OTT-style movie recommender ")

# Load movie data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Fetch poster and details
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path'], data.get('overview', 'No overview'), data.get(
        'release_date', 'N/A'), data.get('vote_average', 'N/A')


# Recommend function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    posters = []
    overviews = []
    release_dates = []
    ratings = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster, overview, release, rating = fetch_poster(movie_id)
        posters.append(poster)
        overviews.append(overview)
        release_dates.append(release)
        ratings.append(rating)

    return recommended_movies, posters, overviews, release_dates, ratings


# Movie selection
selected_movie_name = st.selectbox("Select a movie to get recommendations:", movies['title'].values)

# Recommend button
if st.button("Recommend"):
    names, posters, overviews, release_dates, ratings = recommend(selected_movie_name)

    # Display in 5 columns
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.header(names[idx])
        col.image(posters[idx])
        col.write(f"**Release:** {release_dates[idx]}")
        col.write(f"**Rating:** {ratings[idx]}")
        col.write(overviews[idx])

    # Download CSV
    df = pd.DataFrame({
        "Title": names,
        "Release Date": release_dates,
        "Rating": ratings
    })
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Recommendations", csv,
                       file_name="cine_mate_recommendations.csv",
                       mime="text/csv")
