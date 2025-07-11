from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle

app = Flask(__name__)

with open("data/recommendations.pkl", "rb") as file:
    recommendations = pickle.load(file)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        print("Incoming request JSON:", data)

        if 'movie_id' not in data:
            return jsonify({'error': 'movie_id is required'}), 400

        movie_id = data.get("movie_id")

        try:
            movie_id = int(movie_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'movie_id must be a valid integer'}), 400

        if movie_id not in recommendations:
            return jsonify({'error': f'Movie ID {movie_id} not found'}), 404

        return jsonify({'recommendations': recommendations[movie_id]})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Invalid request format', 'details': str(e)}), 400


@app.route('/movies', methods=['GET'])
def get_movies():
    movie_ids = list(recommendations.keys())[:10]
    return jsonify({'available_movie_ids': movie_ids, 'total_movies': len(recommendations)})


if __name__ == '__main__':
    app.run()
