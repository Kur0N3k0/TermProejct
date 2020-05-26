celery -A tasks.celery worker --loglevel=info --autoscale=10,3
