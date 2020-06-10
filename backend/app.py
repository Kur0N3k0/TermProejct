from flask import Flask, session, redirect, render_template
from appctx import app
from router import prototype
import database

database.initialize()

# default router
@app.route("/")
def main():
    return render_template("/main.html")

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80, debug=True)