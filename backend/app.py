from flask import Flask, session, redirect
from appctx import app
from router import prototype
import database

database.initialize()

# default router
@app.route("/")
def main():
    return redirect("/proto")

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80, debug=True)