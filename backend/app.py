from flask import Flask, session, redirect
from appctx import app
from router import prototype
import database

database.initialize()

# default router
@app.route("/")
def main():
    return redirect("/proto")

@app.route("/test/<float:longtitude>/<float:latitude>/<float:rg>/<int:count>")
def test(longtitude, latitude, rg, count):
    from api.building import Building
    import json
    result = Building().getBuildings(longtitude, latitude, rg, count)
    return json.dumps(result)

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80, debug=True)