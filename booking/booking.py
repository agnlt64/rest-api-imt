from flask import Flask, request, jsonify, make_response
import requests
import json

app = Flask(__name__)

PORT = 3201

def load_bookings():
    with open("./databases/bookings.json", "r") as jsf:
        bookings = json.load(jsf)["bookings"]
    return bookings

def write_bookings(bookings):
    with open("./databases/bookings.json", "w") as f:
        full = {}
        full["movies"] = bookings
        json.dump(full, f)

def error_response(message, code):
    return make_response(jsonify({"error": message}), code)

bookings = load_bookings()

@app.route("/bookings/list/all", methods=["GET"])
def get_all_bookings():
    return make_response(jsonify(bookings))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=True)
