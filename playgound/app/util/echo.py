@app.route(app.config[API_ROOT] + echostring, methods=['GET'])
def echoecho(string)
    return string
