from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle

from helper import get_movie_metadata

app = Flask(__name__)
CORS(app)

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


@app.route("/metadata/<int:movie_id>")
def single_metadata(movie_id):
    data = get_movie_metadata(movie_id)
    return jsonify(data)


@app.route("/metadata_batch", methods=["POST"])
def batch_metadata():
    movie_ids = request.json.get("movie_ids", [])
    results = []

    for movie_id in movie_ids:
        data = get_movie_metadata(movie_id)
        if "error" not in data:
            results.append(data)
    return jsonify(results)


if __name__ == '__main__':
    app.run()
