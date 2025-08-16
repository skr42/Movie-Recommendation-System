import pickle
import streamlit as st
import requests
import base64

# Function to encode image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Encode the image and set as background
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

# Call this before your layout
set_background('netflix.jpg')
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6179e8abe02fd1a06b5ca9f25c0e2885&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=6179e8abe02fd1a06b5ca9f25c0e2885&language=en-US"
    data = requests.get(url).json()
    for video in data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None  # Fallback if no trailer found

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_trailers = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_trailers.append(fetch_trailer(movie_id))
    return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers


st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

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

        .stSelectbox > div {
            background-color: #1e1e2f;
            color: white;
        }

        .stButton>button {
            background-color: #61dafb;
            color: black;
            font-weight: bold;
        }

        .movie-title {
            font-weight: bold;
            color: #61dafb;
            text-align: center;
            margin-top: 10px;
        }

        .stImage img {
            border-radius: 10px;
            transition: transform 0.2s;
        }

        .stImage img:hover {
            transform: scale(1.05);
        }
    </style>

    <div class="title-container">
        <h1>🎬 Movie Recommender System</h1>
    </div>
""", unsafe_allow_html=True)
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_list = movies['title'].values

selected_movie = st.selectbox(
    "🎬 Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    names, posters, trailers = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            trailer_url = trailers[i] if trailers[i] else "#"
            st.markdown(f"""
                <a href="{trailer_url}" target="_blank">
                    <img src="{posters[i]}" width="100%" style="border-radius:10px;" />
                    <div style="text-align:center; color:#61dafb; font-weight:bold; margin-top:5px;">{names[i]}</div>
                </a>
            """, unsafe_allow_html=True)





