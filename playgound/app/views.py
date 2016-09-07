
from app import app
from flask import Flask, jsonify, request, send_from_directory
import json, os, time, hashlib
from .fake import FakeDB, FakeCred

fk = FakeCred()




@app.route(app.config["ABR_ROOT"] + "<school>", methods=['GET'])
def school_url(school):
    s_id = FakeDB("schools").find_id({"url_name":school})
    print s_id
    asset_file = app.config["APP_ROOT"] + "\\assets\\" + s_id + "\\index.html"
    if os.path.isfile(asset_file):
        fs = open(asset_file)
        op = fs.read()

        return op








@app.route(app.config["API_ROOT"] + "echo/<string>", methods=['GET'])
def echoecho(string):
    return string


@app.route(app.config["API_ROOT"] + "user/<user_id>", methods=['GET'])
def _user(user_id):
    pass

@app.route(app.config["API_ROOT"] + "user/create", methods=['POST'])
def create_user():
    jdtg = int(time.time())
    db = FakeDB("users")

    uid = fk.id_generator_from_string(request.values["uname"])

    if db.get(uid):
        op_details = {"error":"user already exists"}
    else:

        if request.values["enroll"]:
            pass


        details = {
            "uname": request.values["uname"],
            "pword": hashlib.sha1(request.values["pword"]).hexdigest(),
            "token": fk.id_generator(32),
            "expire": jdtg + app.config["TOKEN_EXPIRE"],
            "jdtg": jdtg

        }

        op_details = {
            "uname" : details["uname"],
            "token" : details["token"],
            "expire" : details["expire"]
        }
        db.post(uid,details)

    return fk.jsonop(op_details)


@app.route(app.config["API_ROOT"] + "user/update", methods=['POST'])
@fk.require_valid_token()
def update_user():
    no_go = ["token"]
    bla = {}
    id = FakeDB("users").find_value({"token":request.values["token"]})[0]
    for i in request.values:
        if not i in no_go:
            bla[i] = request.values[i]

    details = {id:bla}
    FakeDB("users").update(id, bla)

    return json.dumps(details, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "login", methods=['POST'])
def login():
    db = FakeDB("users")
    uname = fk.id_generator_from_string(request.values['uname'])
    pword = hashlib.sha1(request.values["pword"]).hexdigest()
    if db.get(uname) and db.get(uname)["pword"] == pword:
        details = {"token": fk.id_generator(32),
                   "expire": int(time.time()) + app.config["TOKEN_EXPIRE"]
                  }
        db.update(uname,details)
    else:
        details = {"error" : "login failed"}
    return json.dumps(details, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "logout", methods=['POST'])
def logout():

    try:
        userid = FakeDB("users").find_value({"token" : request.values["token"]})[0]
        FakeDB("users").update(userid, {"expire": int(time.time())})
        details = {"message":"logout"}
    except:
        details = {"message":"error"}

    return json.dumps(details, separators=(',',':'))


@app.route(app.config["API_ROOT"] + "school", methods=['GET'])
def _school():
    return json.dumps({"error":"invalid school id"}, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "school/create", methods=['POST'])
@fk.require_valid_token()
def create_school():
    school_id = fk.id_generator_from_string(request.values["school_name"])
    db = FakeDB("schools")

    if db.get(school_id):
        return json.dumps({"error":"school already exists"}, separators=(',', ':'))

    else:
        c_time = int(time.time())
        c_user = FakeDB("users").find_value({"token":request.values["token"]})[0]
        e_len = 1
        s_key = fk.id_generator_api_key(school_id, c_time)
        s_url = fk.id_generator_cleanname(request.values["school_name"])
        assets_dir = app.config["APP_ROOT"]+"\\assets\\"+school_id

        details = {school_id : {
            "created" : c_time,
            "updated" : c_time,
            "created_by" : c_user,
            "secret_key" : s_key,
            "school_name" : request.values["school_name"],
            "url_name" : s_url
        }}

        op = {school_id : {
            "secret_key" : s_key,
            "school_name" : request.values["school_name"],
            "url" : app.config["URL_ROOT"] + "/@"+ s_url
        }}

        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        db.post(school_id,details)

        FakeDB("enrolls").post(school_id,fk.id_generator_enroll(e_len))

        return json.dumps(op, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "school/update", methods=['POST'])
@fk.require_school_key()
@fk.require_valid_token()
def update_school():

    no_go = ["school_key","school_id","token"]
    bla = {}
    db = FakeDB("schools")
    school_id = request.values["school_id"]

    for i in request.values:
        if not i in no_go:
            bla[i] = request.values[i]

    bla["updated_on"] = int(time.time())
    bla["updated_by"] = FakeDB("users").find_value({"token":request.values["token"]})[0]

    details = {school_id : bla}
    db.update(school_id,bla)

    return json.dumps(details, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "school/<school_id>/<token>", methods=['GET'])
def view_school(school_id,token):
    try:
        school_data = FakeDB("schools").get(school_id)
        if not school_data:
            school_data = {"error":"invalid school id"}
    finally:
        return json.dumps(school_data, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "upload", methods=['POST'])
@fk.require_school_key()
@fk.require_valid_token()
def upload():
    try:
        userid = FakeDB("users").find_value({"token": request.values["token"]})[0]
        f = request.files["file"]
        fext = os.path.splitext(f.filename)
        nfn = fk.id_generator()
        s_id = FakeDB("schools").find_id({""})
        new_file = os.path.join(app.config["APP_ROOT"], app.config['UPLOAD_FOLDER']) + nfn + fext[1]
        f.save(new_file)


        details = {"url": app.config["URL_ROOT"] + app.config["API_ROOT"] + "view/" + nfn + fext[1],
                   "size": os.stat(new_file).st_size,
                   "dtg": int(time.time()),
                   "user": userid
                   }
        FakeDB("upload").post(nfn,details)
    except:
        details = {"error":"upload failed"}

    return json.dumps(details, separators=(',',':'))


@app.route(app.config["API_ROOT"] + "view/<img_name>", methods=['GET'])
def show_uploaded(img_name):
    return send_from_directory(
            os.path.join(
                    app.config["APP_ROOT"],
                    app.config['UPLOAD_FOLDER']
                ),
            img_name
            )
