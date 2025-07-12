from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
from concurrent.futures import ThreadPoolExecutor
from difflib import get_close_matches
from helper import get_movie_metadata

app = Flask(__name__)
CORS(app)

with open("data/recommendations.pkl", "rb") as f1:
    recommendations = pickle.load(f1)

with open("data/horror_dict.pkl", "rb") as f2:
    movie_dict = pickle.load(f2)


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


@app.route('/metadata_batch', methods=["POST"])
def batch_metadata():
    movie_ids = request.json.get("movie_ids", [])
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all jobs in parallel
        future_to_id = {executor.submit(get_movie_metadata, mid): mid for mid in movie_ids}

        for future in future_to_id:
            data = future.result()
            if data:
                results.append(data)

    return jsonify(results)


@app.route('/search/<string:query>', methods=["GET"])
def search_movie(query):
    query_lower = query.lower()

    # Try to find the closest match
    matches = get_close_matches(query_lower, movie_dict.keys(), n=1, cutoff=0.65)

    if matches:
        match = matches[0]
        movie_id = movie_dict[match]
        return jsonify({
            "query": query,
            "matched_title": match,
            "id": movie_id
        })
    else:
        return jsonify({"error": f"No close match found for '{query}'"}), 404


if __name__ == '__main__':
    app.run()
