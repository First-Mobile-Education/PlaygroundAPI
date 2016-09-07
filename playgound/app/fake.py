
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

    def find_id(self,search):
        for a in search:
            sk,sv = a,search[a]
        for items in self.db[self.root]:
            for attr in items.values():
                for x,y in attr.items():
                    for g,h in y.items():
                        if g == sk and h == sv:
                            return x

    def find_value(self,search):

        for sk,sv in search.items():
            for users in self.db[self.root]:
                for attr in users.values():
                    for k,v in attr.items():
                        if k == sk and v == sv:
                            return users.keys()

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

    def jsonop(self, message_string):
        return json.dumps(message_string, separators=(',', ':'))

    def id_generator(self, size=6, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def id_generator_api_key(self, id, mixer):

        return hashlib.sha1(id+str(mixer)).hexdigest()

    def id_generator_from_string(self, encode_string, size=6, leading="0"):
        for i in hashlib.md5(encode_string).hexdigest():
            if i in string.digits:
                leading += i
        return leading[0:size]

    def id_generator_enroll(self, count, clen=10):
        list = []
        for i in range(count):
            a = fk.id_generator(clen)
            if a in list:
                a = fk.id_generator(clen)
            else:
                list[len(list):] = [a]
        return list

    def id_generator_cleanname(self, message_string):
        op = ""
        for i in message_string:
            if i in string.ascii_letters + string.digits:
                op += i

        return op
