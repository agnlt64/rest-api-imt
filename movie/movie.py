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

def is_movie_valid(obj):
    return all([
        obj.get("title"),
        obj.get("rating"),
        obj.get("director"),
        obj.get("id"),
    ])

def get_movie_by_id(id_):
    for movie in movies:
        if movie["id"] == id_:
            return movie
    return None

def get_movie_by_title(title):
    for movie in movies:
        if movie["title"] == title:
            return movie
    return None

@app.route("/movies/list/all", methods=['GET'])
def get_json():
    return make_response(jsonify(movies), 200)

@app.route("/movies/<movieid>", methods=['GET'])
def movie_by_id(movieid):
    movie = get_movie_by_id(movieid)
    if movie is not None:
        return make_response(jsonify(movie), 200)
    return error_response("movie ID not found", 404)

@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()
    if not is_movie_valid(req):
        return error_response("malformed movie body", 400)

    movie = get_movie_by_id(movieid)
    if movie is not None:
        return error_response("movie already exists", 409)

    movies.append(req)
    write_movies(movies)
    res = make_response(jsonify({"message": "movie added"}), 200)
    return res

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    movie = get_movie_by_id(movieid)
    if movie is not None:
        movies.remove(movie)
        write_movies(movies)
        return make_response(jsonify(movie), 200)
    return error_response("movie ID not found", 404)

# /info?title=...
@app.route("/movies/info", methods=['GET'])
def movie_by_title():
    movie = get_movie_by_title(request.args.get("title"))
    if movie is not None:
        return make_response(jsonify(movie), 200)
    return error_response("movie title not found", 404)

# new rating is in request body
@app.route("/movies/rating/<movieid>", methods=['PUT'])
def update_movie_rating(movieid):
    req = request.get_json()
    movie = get_movie_by_id(movieid)
    if movie is not None:
        movie["rating"] = req["rating"]
        write_movies(movies)
        return make_response(jsonify(movie), 200)
    return error_response("movie ID not found", 404)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=PORT, debug=True)
