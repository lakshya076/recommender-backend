import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_movie_metadata(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return {"error": "Movie not found"}
    return {"error": "Movie not found"}
