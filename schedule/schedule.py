from flask import Flask, request, jsonify, make_response
import json
import requests

app = Flask(__name__)

PORT = 3202

def load_schedule():
   with open("./databases/times.json", "r") as jsf:   
      schedule = json.load(jsf)["schedule"]
   return schedule

def write_schedule(schedule):
   with open("./databases/times.json", 'w') as f:
      full = {}
      full['schedule'] = schedule
      json.dump(full, f)

schedule = load_schedule()

def error_response(message, code):
    return make_response(jsonify({"error": message}), code)

def get_movies_by_date(date):
   for entry in schedule:
      if entry["date"] == date:
         return entry
   return []

# in the request body we expect { date: "", movies: [] }
def is_body_valid(body):
   date = body.get("date")
   movies = body.get("movies")
   example_date = "20260101"
   if date is None or movies is None or len(date) != len(example_date) or type(movies) != list:
      return False
   return True

def get_valid_movies(movies):
   for movie_id in movies:
      resp = requests.get(f"http://127.0.0.1:3200/movies/{movie_id}")
      if resp.status_code == 404:
         movies.remove(movie_id)
   return movies

@app.route("/schedule/list/all", methods=['GET'])
def get_all_schedules():
   return make_response(jsonify(schedule))

@app.route("/schedule/<date>", methods=["GET"])
def get_date(date):
   if len(movies := get_movies_by_date(date)) != 0:
      return make_response(jsonify(movies), 200)
   return error_response("no movies for the given date", 404)

@app.route("/schedule/<date>", methods=["POST"])
def add_movies_to_schedule(date):
   body = request.get_json()
   if not is_body_valid(body):
      return error_response("malformed request body", 400)
   
   movies_from_req = body.get("movies")
   if len(movies_from_req) == 0:
      return error_response("no movies were specified", 400)
   
   movies_to_add = get_valid_movies(movies_from_req)
   if len(existing_entry := get_movies_by_date(date)) != 0:
      existing_entry["movies"] = list(set(existing_entry["movies"]) | set(movies_to_add))
      write_schedule(schedule)
      return make_response(jsonify(existing_entry), 200)
   else:
      new_entry = {
         "date": date,
         "movies": movies_to_add,
      }
      schedule.append(new_entry)
      write_schedule(schedule)
   return make_response(jsonify(new_entry), 200)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=PORT, debug=True)