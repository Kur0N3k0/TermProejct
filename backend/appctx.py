from flask import Flask
from database import mongo
import json

# load config
config = json.load(open("./config.json"))

app = Flask(__name__)
app.config["MONGO_URI"] = config["database"]
app.config['UPLOAD_FOLDER'] = config["upload"]
app.secret_key = config["flask"]["secretkey"].encode()
mongo.init_app(app)