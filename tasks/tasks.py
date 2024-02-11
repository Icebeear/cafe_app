import asyncio

from celery import Celery

from tasks.update_db import update_db_online

app = Celery('tasks', backend='rpc://', broker='pyamqp://')

app.conf.beat_schedule = {
    'synchronize-every-15-seconds': {
        'task': 'tasks.tasks.db_synchronization',
        'schedule': 15.0,
    },
}


@app.task
def db_synchronization():
    asyncio.run(update_db_online())
