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

@app.route("/api/create/projectnames/<userid>", methods=["POST"])
def create_project(userid):
    projectname = request.form.get("projectname")
    with open(f"{APP_ROOT}/db/projectnames.json", "r") as json_file:
        projectnames = json.load(json_file)
        projectnames_backup = copy.deepcopy(projectnames)
    with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
        projects = json.load(json_file)
        projects_backup = copy.deepcopy(projects)
    if userid in projectnames.keys():
        projectid = uuid7str()
        projectnames[userid]["projectnames"].insert(0,{
            "projectid": projectid,
            "projectname": projectname
        })
        projects.update({
            projectid: {}
        })
        try:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames, json_file, indent=2)
            with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                json.dump(projects, json_file, indent=2)
            res = {
                "status": "ok",
                "message": "Project created!",
                "projectid": projectid
            }
            return jsonify(res)
        except Exception:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames_backup, json_file, indent=2)
            with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                json.dump(projects_backup, json_file, indent=2)
            res = {
                "status": "not-ok",
                "message": "Project could not be created!"
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
        projects.update({
            projectid: {}
        })
        try:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames, json_file, indent=2)
            with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                json.dump(projects, json_file, indent=2)
            res = {
                "status": "ok",
                "message": "Project created!",
                "projectid": projectid
            }
            return jsonify(res)
        except Exception:
            with open(f"{APP_ROOT}/db/projectnames.json", "w") as json_file:
                json.dump(projectnames_backup, json_file, indent=2)
            with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                json.dump(projects_backup, json_file, indent=2)
            res = {
                "status": "not-ok",
                "message": "Project cannot be created!"
            }
            return jsonify(res)

@app.route("/api/get/projectnames/<userid>", methods=["POST"])
def get_projectnames(userid):
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

@app.route("/api/get/project/<userid>/<projectid>", methods=["POST"])
def get_project(userid, projectid):
    with open(f"{APP_ROOT}/db/projectnames.json", "r") as json_file:
        projectnames = json.load(json_file)
    with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
        projects = json.load(json_file)
    projectname = ""
    projectdetails = {}
    if userid in projectnames.keys():
        for project in projectnames[userid]["projectnames"]:
            if project["projectid"] == projectid:
                projectname = project["projectname"]
                break
    else:
        res = {
            "status": "not-ok",
            "message": "Something went wrong!"
        }
        return jsonify(res)
    if projectid in projects.keys():
        projectdetails = projects[projectid]
        res = {
            "status": "ok",
            "projectname": projectname,
            "projectdetails": projectdetails
        }
        return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Project not found!"
        }
        return jsonify(res)

@app.route("/api/adddata/<category>/<projectid>", methods=["POST"])
def add_data_to_project(category, projectid):
    if request.method == "POST":
        formdata = request.form
        if not formdata:
            res = {
                "status": "not-ok",
                "message": "No form data found!"
            }
            return jsonify(res)
        new_data = {
            "id": uuid7str()
        }
        for key, value in formdata.to_dict().items():
            new_data.update({key: value})
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
            projects_backup = copy.deepcopy(projects)
        if projectid in projects.keys():
            try:
                if category in projects[projectid].keys():
                    projects[projectid][category].append(new_data)
                else:
                    projects[projectid][category] = []
                    projects[projectid][category].append(new_data)
                with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                    json.dump(projects, json_file, indent=2)
                res = {
                    "status": "ok",
                    "message": "Data added!"
                }
                return jsonify(res)
            except Exception:
                with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                    json.dump(projects_backup, json_file, indent=2)
                res = {
                    "status": "not-ok",
                    "message": "Could not add data!"
                }
                return jsonify(res)
        else:
            res = {
                "status": "not-ok",
                "message": "Project not found!"
            }
            return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Unsupported HTTP method!"
        }
        return jsonify(res)

@app.route("/api/delete/<projectid>/<category>/<dataid>", methods=["POST"])
def delete_data_from_project(projectid, category, dataid):
    with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
        projects = json.load(json_file)
        projects_backup = copy.deepcopy(projects)
    for entry in projects[projectid][category]:
        if entry["id"] == dataid:
            projects[projectid][category].remove(entry)
            break
    try:
        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
            json.dump(projects, json_file, indent=2)
        res = {
            "status": "ok",
            "message": "Data deleted!"
        }
        return jsonify(res)
    except Exception:
        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
            json.dump(projects_backup, json_file, indent=2)
        res = {
            "status": "not-ok",
            "message": "Could not delete data!"
        }
        return jsonify(res)

@app.route("/api/project/<projectid>", methods=["POST"])
def get_project_details(projectid):
    if request.method == "POST":
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
        res = {
            "status": "ok",
            "project": projects[projectid]
        }
        return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Unsupported HTTP method!"
        }
        return jsonify(res)

@app.route("/api/project/<projectid>/<category>", methods=["POST"])
def get_category_details(projectid, category):
    if request.method == "POST":
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
        res = {
            "status": "ok",
            category: projects[projectid][category]
        }
        return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Unsupported HTTP method!"
        }
        return jsonify(res)

@app.route("/api/project/<projectid>/<category>/<dataid>", methods=["POST", "PUT", "DELETE"])
def data_record(projectid, category, dataid):
    if request.method == "POST":
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
        if projectid in projects.keys() and category in projects[projectid].keys():
            for data in projects[projectid][category]:
                if data["id"] == dataid:
                    res = {
                        "status": "ok",
                        "data": data
                    }
                    return jsonify(res)
            else:
                res = {
                    "status": "not-ok",
                    "message": "Data not found!"
                }
                return jsonify(res)
        else:
            res = {
                "status": "not-ok",
                "message": "Data not found!"
            }
            return jsonify(res)
    elif request.method == "PUT":
        formdata = request.form
        if not formdata:
            res = {
                "status": "not-ok",
                "message": "No form data found!"
            }
            return jsonify(res)
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
            projects_backup = copy.deepcopy(projects)
        if projectid in projects.keys() and category in projects[projectid].keys():
            for data in projects[projectid][category]:
                if data["id"] == dataid:
                    for key, value in formdata.to_dict().items():
                        data[key] = value
                    try:
                        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                            json.dump(projects, json_file, indent=2)
                        res = {
                            "status": "ok",
                            "message": "Data record updated!"
                        }
                        return jsonify(res)
                    except Exception:
                        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                            json.dump(projects_backup, json_file, indent=2)
                        res = {
                            "status": "not-ok",
                            "message": "Could not update record!"
                        }
                        return jsonify(res)
                else:
                    res = {
                        "status": "not-ok",
                        "message": "Data not found!"
                    }
                    return jsonify(res)
        else:
            res = {
                "status": "not-ok",
                "message": "Data not found!"
            }
            return jsonify(res)
    elif request.method == "DELETE":
        with open(f"{APP_ROOT}/db/projects.json", "r") as json_file:
            projects = json.load(json_file)
            projects_backup = copy.deepcopy(projects)
        if projectid in projects.keys() and category in projects[projectid].keys():
            for data in projects[projectid][category]:
                if data["id"] == dataid:
                    projects[projectid][category].remove(data)
                    try:
                        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                            json.dump(projects, json_file, indent=2)
                        res = {
                            "status": "ok",
                            "message": "Data record deleted!"
                        }
                        return jsonify(res)
                    except Exception:
                        with open(f"{APP_ROOT}/db/projects.json", "w") as json_file:
                            json.dump(projects_backup, json_file, indent=2)
                        res = {
                            "status": "not-ok",
                            "message": "Could not delete record!"
                        }
                        return jsonify(res)
                else:
                    res = {
                        "status": "not-ok",
                        "message": "Data not found!"
                    }
                    return jsonify(res)
        else:
            res = {
                "status": "not-ok",
                "message": "Data not found!"
            }
            return jsonify(res)
    else:
        res = {
            "status": "not-ok",
            "message": "Unsupported HTTP method!"
        }
        return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)