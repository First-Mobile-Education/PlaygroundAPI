#!flask/bin/python
from flask import Flask, jsonify, request, send_from_directory
import json, os, random, string, time, hashlib

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "upload\\"
app.config["DATABASE_FOLDER"] = "\\db\\"
app.config["APP_ROOT"] = os.path.dirname(os.path.abspath(__file__))
app.config["URL_ROOT"] = "http://localhost:5000"
app.config["PROJECT"] = "playground"
app.config["VERSION"] = "1.0"
app.config["TOKEN_EXPIRE"] = 86400 # 24 hours
app.config["API_ROOT"] = "/" + app.config["PROJECT"]+"/api/v"+app.config["VERSION"]+"/"


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

    def post(self,key,value):
        try:
            self.db[self.root].append({key:value})
            self.save()
            return True
        except:
            return False

    def find_value(self,search):
        # db
        #  |->root
        #        |->index
        #               |->key = value

        # return index of found value
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
            else:
                return False

    def update(self,key,entry):
        try:
            for i in self.db[self.root]:
                if i.keys()[0] == key:
                    for a in entry.keys():
                        i[key][a] = entry[a]
                else:
                    return False
            self.save()
            return True
        except:
            return False

    def save(self):
        self.db_file.seek(0)
        self.db_file.write(json.dumps(self.db, separators=(',', ':')))

    def __str__(self):
        return self.root

def id_generator(size=6, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


# GET functions

@app.route(app.config["API_ROOT"] + "view/<img_name>", methods=['GET'])
def show_uploaded(img_name):
    return send_from_directory(
            os.path.join(
                    app.config["APP_ROOT"],
                    app.config['UPLOAD_FOLDER']
                ),
            img_name
            )


# POST functions

@app.route(app.config["API_ROOT"] + "login", methods=['POST'])
def login_user():
    db = FakeDB("users")
    uname = hashlib.md5(request.values["uname"]).hexdigest()
    pword = hashlib.sha1(request.values["pword"]).hexdigest()
    if db.get(uname) and db.get(uname)["pword"] == pword:
        details = {"token": id_generator(32),
                    "expire": int(time.time()) + app.config["TOKEN_EXPIRE"]
                       }

        print db.update(uname,details)
    else:
        details = {"login":"failed"}

    return json.dumps(details, separators=(',', ':'))


@app.route(app.config["API_ROOT"] + "logout", methods=['POST'])
def logout():

    token = "fKab3xommLoFFQfKy46bK3lPPorWWdTR"

    return jsonify(FakeDB("users").find_value(token))





    """
    try:
        if FakeDB("users").get(request.values["userid"])["token"] == request.values["token"]:
            FakeDB("users").update(request.values["userid"],{"expire":int(time.time())})
            return json.dumps({"message":"logout"}, separators=(',', ':'))
    except:
        return json.dumps({"error":"logout error"}, separators=(',', ':'))
    """

@app.route(app.config["API_ROOT"] + "upload", methods=['POST'])
def get_upload():
    try:
        if FakeDB("users").get(request.values["userid"])["token"] == request.values["token"]:
            f =  request.files["file"]
            fext = os.path.splitext(f.filename)
            nfn = id_generator()
            new_file = os.path.join(app.config["APP_ROOT"], app.config['UPLOAD_FOLDER']) + nfn + fext[1]
            f.save(new_file)
            details = {"url": app.config["URL_ROOT"] + app.config["API_ROOT"] + "view/" + nfn + fext[1],
                       "size": os.stat(new_file).st_size,
                       "dtg": int(time.time()),
                       "user": request.values["userid"]
                       }
            FakeDB("upload").post(nfn,details)
        else:
            details = {"error":"upload failed"}
    except:
        details = {"error":"upload failed"}

    return json.dumps(details, separators=(',',':'))


@app.route(app.config["API_ROOT"] + "create/user", methods=['POST'])
def create_user():
    jdtg = int(time.time())
    db = FakeDB("users")
    uid = hashlib.md5(request.values["uname"]).hexdigest()
    if db.get(uid):
        details = {"error":"user already exists"}
    else:
        details = {
            "uname": request.values["uname"],
            "pword": hashlib.sha1(request.values["pword"]).hexdigest(),
            "token": id_generator(32),
            "expire": jdtg + app.config["TOKEN_EXPIRE"],
            "jdtg": jdtg
        }
        db.post(uid,details)

    return json.dumps(details, separators=(',', ':'))


if __name__ == "__main__":

    app.run(debug=True)