from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'


with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def read():
	with open('{}/databases/users.json'.format("."), "r") as jsf:
		users = json.load(jsf)["users"]
	return users

def write(users):
	with open('{}/databases/users.json'.format("."), 'w') as f:
		full = {}
		full['users']=users
		json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
	return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/users/create-user/<user_id>", methods=['POST'])
def create_user(user_id):
	req = request.get_json()

	for user in users:
		if str(user["id"]) == str(user_id):
				print(user["id"])
				print(user_id)
				return make_response(jsonify({"error":"user ID already exists"}),400)

	users.append(req)
	write(users)
	res = make_response(jsonify({"message":"user added"}),200)
	return res


@app.route("/users/read-all-users", methods=['GET'])
def read_all_users():
	users = read()
	res = make_response(jsonify(users),200)
	return res


@app.route("/users/update-user/<user_id>", methods=['PUT'])
def update_user(user_id, name):
	for user in users:
		if str(user["id"]) == str(user_id):
			user["name"] = name
			res = make_response(jsonify(user),200)
			write(users)
			return res

	res = make_response(jsonify({"error":"user ID not found"}),500)
	return res


@app.route("/users/delete-user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
	for user in users:
		if str(user["id"]) == str(user_id) and str(user["role"]) == "user":
			users.remove(user)
			write(users)
			res = make_response(jsonify({"message":"user deleted"}),200)
			return res

	res = make_response(jsonify({"error":"user ID not found"}),500)
	return res



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
