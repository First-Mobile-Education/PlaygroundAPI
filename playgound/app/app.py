#!flask/bin/python
# BS22NF

from flask import Flask, jsonify, request, send_from_directory
from functools import wraps
import json, os, random, string, time, hashlib


class FakeDB:
    # FakeDB (C)2016

    def __init__(self,db_name):
        self.root = db_name
        db_path = os.path.dirname(os.path.abspath(__file__)) + "\\db\\" + self.root + ".json"
        if os.path.isfile(db_path):
            self.db_file = open(db_path,"r+")
            try:
                self.db = json.loads(self.db_file.read())
            except:
                self.db = json.loads("{\"" + self.root + "\":[]}")
        else:
            self.db_file = open(db_path, "w+")
            self.db = json.loads("{\"" + self.root + "\":[]}")

    def __str__(self):
        return self.root

    def post(self,key,value):
        try:
            self.db[self.root].append({key:value})
            self.save()
            return True
        except:
            return False

    def find_value(self,search):
        try:
            for sk,sv in search.items():
                for users in self.db[self.root]:
                    for attr in users.values():
                        for k,v in attr.items():
                            if k == sk and v == sv:
                                return users.keys()
        except:
            return False

    def get(self,key):
        for i in self.db[self.root]:
            if i.keys()[0] == key:
                return i[key]

    def update(self,key,entry):

        try:
            for i in range(len(self.db[self.root])):
                if self.db[self.root][i].keys()[0] == key:
                    for a in entry: self.db[self.root][i][key][a] = entry[a]
            self.save()
            return True
        except:
            return False

    def save(self):
        self.db_file.seek(0)
        self.db_file.write(json.dumps(self.db, separators=(',', ':')))

class FakeCred:
    # FakeCred (C)2016

    def require_valid_token(self):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                try:
                    id = FakeDB("users").find_value({"token": request.values["token"]})[0]
                    if FakeDB("users").get(id)["expire"] > int(time.time()):
                        func = f(*args, **kwargs)
                        return func
                    else:
                        return json.dumps({"error":"expired token"}, separators=(',', ':'))
                except:
                    return json.dumps({"error": "token error"}, separators=(',', ':'))
            return wrapped
        return decorator

    def require_school_key(self):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # print request.values["school_key"]
                id = request.values["school_id"]
                key = request.values["school_key"]
                if FakeDB("schools").get(id)[id]["secret_key"] == key:
                    func = f(*args, **kwargs)
                    return func
                else:
                    return json.dumps({"error": "api error"}, separators=(',', ':'))
            return wrapped
        return decorator



    def id_generator(self, size=6, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def id_generator_api_key(self,id,mixer):

      return hashlib.sha1(id+str(mixer)).hexdigest()

    def id_generator_from_string(self, encode_string, size=6, leading="0"):
        for i in hashlib.md5(encode_string).hexdigest():
            if i in string.digits:
                leading += i
        return leading[0:size]


fk = FakeCred()
app = Flask(__name__)


app.config["IP"] = "127.0.0.1"
app.config["HTTP_TYPE"] = "http"
app.config["HTTP_PORT"] = "5000"

app.config["UPLOAD_FOLDER"] = "upload\\"
app.config["DATABASE_FOLDER"] = "\\db\\"

app.config["APP_ROOT"] = os.path.dirname(os.path.abspath(__file__))
app.config["PROJECT"] = "playground"
app.config["VERSION"] = "1.0"

app.config["TOKEN_EXPIRE"] = (60 * 60 * 24) # 24 HOURS

app.config["API_ROOT"] = "/" + app.config["PROJECT"] + "/api/v" + app.config["VERSION"] + "/"

app.config["URL_ROOT"] = app.config["HTTP_TYPE"] + "://" + \
                         app.config["IP"] + ":" + \
                         app.config["HTTP_PORT"]




@app.route(app.config["API_ROOT"] + "@<token>", methods=['GET'])
def user(token):
    try:
        if FakeDB("users").find_value({"token":token})[0]:
            return json.dumps({"data": "true"}, separators=(',', ':'))
    except:
        return json.dumps({"data": "false"}, separators=(',', ':'))


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

    return json.dumps(op_details, separators=(',', ':'))


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

        details = {school_id : {
            "created_on" : c_time,
            "updated_on" : c_time,
            "created_by" : c_user,
            "secret_key" : fk.id_generator_api_key(school_id, c_time),
            "owner" : [c_user],
            "school_name" : request.values["school_name"]
        }}
        db.post(school_id,details)

        return json.dumps(details, separators=(',', ':'))


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
@fk.require_valid_token()
def upload():
    try:
        userid = FakeDB("users").find_value({"token": request.values["token"]})[0]
        f = request.files["file"]
        fext = os.path.splitext(f.filename)
        nfn = fk.id_generator()
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


if __name__ == "__main__":

    app.run(debug=True)