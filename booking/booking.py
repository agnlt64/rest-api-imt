from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write_bookings_to_file():
    with open('{}/databases/bookings.json'.format("."), "w") as jsf:
        json.dump({"bookings": bookings}, jsf, indent=4)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings/create-booking/<booking_id>", methods=['POST'])
def create_booking(booking_id):
	req = request.get_json()

	for booking in bookings:
		if str(booking["id"]) == str(booking_id):
			return make_response(jsonify({"error":"booking ID already exists"}),400)

	bookings.append(req)
	write_bookings_to_file()
	res = make_response(jsonify({"message":"booking added"}),200)
	return res

@app.route("/bookings/read-all-bookings", methods=['GET'])
def read_all_bookings():
   res = make_response(jsonify(bookings),200)
   return res

@app.route("/bookings/delete-booking/<booking_id>", methods=['DELETE'])
def delete_booking(booking_id):
	for booking in bookings:
		if str(booking["id"]) == str(booking_id):
			write_bookings_to_file()
			bookings.remove(booking)
			res = make_response(jsonify({"message":"booking deleted"}),200)
			return res

	res = make_response(jsonify({"error":"booking ID not found"}),500)
	return res

@app.route("/bookings/get-detailed-booking/<booking_id>", methods=['GET'])
def get_detailed_booking(booking_id):
	for booking in bookings:
		if str(booking["id"]) == str(booking_id):
			res = make_response(jsonify(booking),200)
			return res

	res = make_response(jsonify({"error":"booking ID not found"}),500)
	return res


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
