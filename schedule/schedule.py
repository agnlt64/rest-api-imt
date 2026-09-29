from flask import Flask, render_template, request, jsonify, make_response
import json

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

@app.route("/schedule/list/all", methods=['GET'])
def get_all_schedules():
   return make_response(jsonify(schedule))

@app.route("/schedule/<date>", methods=["GET"])
def get_date(date):
   if len(movies := get_movies_by_date(date)) != 0:
      return make_response(jsonify(movies), 200)
   return error_response("no movies for the given date", 404)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=PORT, debug=True)