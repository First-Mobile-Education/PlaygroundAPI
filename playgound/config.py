# -*- coding: utf8 -*-
# BS22NF

import os

IP = "127.0.0.1"

HTTP_TYPE = "http"

HTTP_PORT = "5000"

UPLOAD_FOLDER = "upload\\"

DATABASE_FOLDER = "\\db\\"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

PROJECT = "playground"

VERSION = "1.0"

TOKEN_EXPIRE = (60 * 60 * 24) # 24 HOURS

API_ROOT = "/" + PROJECT + "/api/v" + VERSION + "/"

URL_ROOT = HTTP_TYPE + "://" + IP + ":" + HTTP_PORT

ABR_ROOT = "/@"