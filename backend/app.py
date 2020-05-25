from flask import Flask, session
from appctx import app
from router import prototype

# default router
@app.route("/")
def main():
    session["test"] = 1
    return ""

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80)