from flask import Flask, session, redirect, render_template, send_file
from appctx import app
from router import prototype
import database, os

database.initialize()

# default router
@app.route("/")
def main():
    return render_template("/main.html")

@app.route("/image/<path>")
def imageLink(path):
    return send_file(os.path.join(app.config["UPLOAD_FOLDER"], path))

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80, debug=True)
