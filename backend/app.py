from flask import Flask, session, redirect
from appctx import app
from router import prototype
import database

database.initialize()

# default router
@app.route("/")
def main():
    return redirect("/proto")

@app.route("/test/<float:longtitude>/<float:latitude>/<int:rg>")
def test(longtitude, latitude, rg):
    from api.cctv import cctvAPI

    result = cctvAPI().getCCTVByLocation(longtitude, latitude, rg)
    print(result)
    return "haha"

# add router
app.register_blueprint(prototype.router, url_prefix="/proto")

app.run(host="0.0.0.0", port=80, debug=True)