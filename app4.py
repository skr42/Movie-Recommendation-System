import pickle
import streamlit as st
import requests
import base64


# Background image setup
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background('netflix.jpg')


# TMDB API fetchers
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6179e8abe02fd1a06b5ca9f25c0e2885&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""


def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=6179e8abe02fd1a06b5ca9f25c0e2885&language=en-US"
    data = requests.get(url).json()
    for video in data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


# Recommendation engine
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters, trailers, tmdb_links = [], [], [], []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        trailer = fetch_trailer(movie_id)
        trailers.append(trailer if trailer else "#")
        tmdb_links.append(f"https://www.themoviedb.org/movie/{movie_id}")

    return names, posters, trailers, tmdb_links


# Page style and header
st.markdown("""
    <style>
        .title-container {
            background-color: #1f1f2e;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .title-container h1 {
            color: #61dafb;
            font-size: 3em;
        }
        .stButton>button {
            background-color: #61dafb;
            color: black;
            font-weight: bold;
        }
        .stImage img {
            border-radius: 10px;
            transition: transform 0.2s;
        }
        .stImage img:hover {
            transform: scale(1.05);
        }
        .movie-title a {
            color: #61dafb;
            font-weight: bold;
            text-decoration: none;
        }
        .movie-title a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="title-container">
        <h1>🎬 Movie Recommender System</h1>
    </div>
""", unsafe_allow_html=True)

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Type or select a movie from the dropdown", movie_list)

# Show recommendation section
if st.button('Show Recommendation'):
    names, posters, trailers, tmdb_links = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.markdown(f"""
                <a href="{trailers[i]}" target="_blank">
                    <img src="{posters[i]}" width="100%" style="border-radius:10px;" />
                </a>
                <div class="movie-title" style="text-align:center; margin-top:5px;">
                    <a href="{tmdb_links[i]}" target="_blank">{names[i]}</a>
                </div>
            """, unsafe_allow_html=True)
