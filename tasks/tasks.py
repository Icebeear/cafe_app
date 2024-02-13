import asyncio

from celery import Celery

from tasks.update_db import db_updater

app = Celery('tasks', backend='rpc://', broker='pyamqp://')

app.conf.beat_schedule = {
    'synchronize-every-15-seconds': {
        'task': 'tasks.tasks.db_synchronization',
        'schedule': 15.0,
    },
}


@app.task
def db_synchronization():
    asyncio.run(db_updater.update_db_online())
