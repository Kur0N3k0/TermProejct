from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from database import task_redis, mongo
import uuid, json
import tasks

router = Blueprint("proto", __name__)

@router.route("/")
def main():
    return "main"

################################################
# Celery front task...
# information lifecycle
# expire: 1 day
################################################
@router.route("/region/safety/<region>")
def regionSafety(region):
    cached = task_redis.get(region)
    if not cached:
        task = tasks.getRegionSafety.apply_async(args=(region,))

        info = json.dumps({
            "taskid": task.id,
            "result": ""
        })

        task_redis.set(region, info, ex=3600 * 24) # 1 day
        return f"task accepted({task.id})"
    return cached

@router.route("/region/safety/<region>/get")
def getRegionSafety(region):
    cached = task_redis.get(region)
    if not cached:
        return "not yet"
    
    cached = json.loads(cached)
    taskid = cached["taskid"]
    task = tasks.getRegionSafety.AsyncResult(taskid)
    if task.state == "PROGRESS":
        return task.info
    elif task.state != "FAILURE":
        cached["result"] = task.info
        cached = json.dumps(cached)
        task_redis.set(region, cached)
        return cached
    return "failed.."