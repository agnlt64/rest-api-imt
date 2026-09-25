from flask import Flask, request, jsonify, make_response
import json

app = Flask(__name__)

PORT = 3200

def load_movies():
    movies = []
    with open('./databases/movies.json', 'r') as jsf:
        movies = json.load(jsf)["movies"]
    return movies

def write_movies(movies):
    with open('./databases/movies.json', 'w') as f:
        full = {}
        full['movies']=movies
        json.dump(full, f)

def error_response(message, code):
    return make_response(jsonify({"error": message}), code)

movies = load_movies()

@app.route("/movies/list/all", methods=['GET'])
def get_json():
    return make_response(jsonify(movies), 200)

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_by_id(movieid):
    for movie in movies:
        # movie is an object from DB, it's guaranteed to have an id
        if movie["id"] == movieid:
            res = make_response(jsonify(movie), 200)
            return res
    return error_response("movie ID not found", 404)

@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()
    try:
        req["title"]
        req["rating"]
        req["director"]
        req["id"]
    except KeyError:
        return error_response("malformed movie body", 400)

    for movie in movies:
        if movie["id"] == movieid:
            return error_response("movie already exists", 409)

    movies.append(req)
    write_movies(movies)
    res = make_response(jsonify({"message": "movie added"}), 200)
    return res

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if movie["id"] == movieid:
            movies.remove(movie)
            write_movies(movies)
            return make_response(jsonify(movie), 200)

    return error_response("movie ID not found", 404)

# /info?title=...
@app.route("/movies/info", methods=['GET'])
def get_movie_by_title():
    for movie in movies:
        if movie["title"] == request.args.get("title"):
            return make_response(jsonify(movie), 200)

    return error_response("movie title not found", 404)

# new rating is in request body
@app.route("/movies/rating/<movieid>", methods=['PUT'])
def update_movie_rating(movieid):
    req = request.get_json()
    for movie in movies:
        if movie["id"] == movieid and (rating := req["rating"]):
            movie["rating"] = rating
            write_movies(movies)
            return make_response(jsonify(movie), 200)

    return error_response("movie ID not found", 404)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=PORT, debug=True)
