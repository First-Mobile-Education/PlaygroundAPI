# BS22NF

from flask import Flask, jsonify, request, send_from_directory
from functools import wraps
import json, os, random, string, time, hashlib
from .fake import FakeDB, FakeCred

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

app.config["ABR_ROOT"] = "/@"

import views
