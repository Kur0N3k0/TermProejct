from celery import Celery
from appctx import app
from api.safety import SafetyAPI

BROKER = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
celery = Celery("tasks", broker=BROKER, backend=CELERY_RESULT_BACKEND)

################################################
# Celery backend task...
# 
################################################
@celery.task(bind=True)
def getRegionSafety(self, region):
    with app.app_context():
        # start business logic
        self.update_state(state="PROGRESS", meta="progress..")

        safety_api = SafetyAPI()
        return safety_api.getSafetyByRegionCode(region)