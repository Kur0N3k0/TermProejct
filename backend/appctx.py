from flask import Flask
import json

# load config
config = json.load(open("./config.json"))

app = Flask(__name__)
app.config["MONGO_URI"] = config["database"]
app.secret_key = config["flask"]["secretkey"].encode()