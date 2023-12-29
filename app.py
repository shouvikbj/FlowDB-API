from flask import Flask, jsonify, request
from uuid_extensions import uuid7str
import os
import json
import copy
from flask_cors import CORS
from gp_hashing.generateHash import generateHash

app = Flask(__name__, static_url_path="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = "thisisasecretkey"
CORS(app, origins="*")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/", methods=["GET", "POST"])
def default():
    return "<h1 style='text-align:center'>404<h1>"

@app.route("/api", methods=["GET", "POST"])
def default_api():
    return "<h1 style='text-align:center'>404<h1>"

@app.route("/api/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    password = generateHash(request.form.get("password"))
    userid = uuid7str()
    new_user = {
        userid: {
            "name": name,
            "email": email,
            "password": password
        }
    }
    with open(f"{APP_ROOT}/db/users.json", "r") as json_file:
        users = json.load(json_file)
        users_backup = copy.deepcopy(users)
    for _, user in users.items():
        if user["email"] == email:
            res = {
                "status": "not-ok",
                "message": "Email already in use!"
            }
            return jsonify(res)
    try:
        users.update(new_user)
        with open(f"{APP_ROOT}/db/users.json", "w") as json_file:
            json.dump(users, json_file, indent=2)
        res = {
            "status": "ok",
            "message": "Account created!"
        }
        return jsonify(res)
    except Exception:
        with open(f"{APP_ROOT}/db/users.json", "w") as json_file:
            json.dump(users_backup, json_file, indent=2)
        res = {
            "status": "not-ok",
            "message": "Could not create account!"
        }
        return jsonify(res)

@app.route("/api/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    with open(f"{APP_ROOT}/db/users.json", "r") as json_file:
        users = json.load(json_file)
    for id, user in users.items():
        if user["email"] == email and user["password"] == generateHash(password):
            res = {
                "status": "ok",
                "userid": id
            }
            return jsonify(res)
        elif user["email"] == email and not (user["password"] == generateHash(password)):
            res = {
                "status": "not-ok",
                "message": "Email and password doesn't match!"
            }
            return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Cannot find your account!"
        }
        return jsonify(res)

@app.route("/api/get/user/<userid>", methods=["POST"])
def get_user_details(userid):
    with open(f"{APP_ROOT}/db/users.json", "r") as json_file:
        users = json.load(json_file)
    if userid in users.keys():
        res = {
            "status": "ok",
            "user": users[userid]
        }
        return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "User not found!"
        }
        return jsonify(res)

@app.route("/api/create/project/<userid>", methods=["POST"])
def create_project(userid):
    projectname = request.form.get("projectname")
    with open(f"{APP_ROOT}/db/projectnames.json", "r") as json_file:
        projectnames = json.load(json_file)
        projectnames_backup = copy.deepcopy(projectnames)
    if userid in projectnames.keys():
        projectid = uuid7str()
        projectnames[userid]["projectnames"].insert(0,{
            "projectid": projectid,
            "projectname": projectname
        })
        try:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames, json_file, indent=2)
            res = {
                "status": "ok",
                "message": "Project created!",
                "projectid": projectid
            }
            return jsonify(res)
        except Exception:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames_backup, json_file, indent=2)
            res = {
                "status": "not-ok",
                "message": "Project cannot be created!"
            }
            return jsonify(res)
    else:
        projectid = uuid7str()
        projectnames.update({
            userid: {
                "projectnames": [
                    {
                        "projectid": projectid,
                        "projectname": projectname
                    }
                ]
            }
        })
        try:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames, json_file, indent=2)
            res = {
                "status": "ok",
                "message": "Project created!",
                "projectid": projectid
            }
            return jsonify(res)
        except Exception:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames_backup, json_file, indent=2)
            res = {
                "status": "not-ok",
                "message": "Project cannot be created!"
            }
            return jsonify(res)

@app.route("/api/get/projects/<userid>", methods=["POST"])
def get_projects(userid):
    with open(f"{APP_ROOT}/db/projectnames.json", "r") as json_file:
        projectnames = json.load(json_file)
    if userid not in projectnames.keys():
        res = {
            "status": "not-ok",
            "message": "No projects found!"
        }
        return jsonify(res)
    else:
        res = {
            "status": "ok",
            "projectnames": projectnames[userid]["projectnames"]
        }
        return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)