from celery import Celery

from tasks.task_online import google_task_online

app = Celery('tasks', backend='rpc://', broker='pyamqp://')

app.conf.beat_schedule = {
    'synchronize-every-15-seconds': {
        'task': 'tasks.tasks.google_sheet_synchronization',
        'schedule': 15.0,
    },
}


@app.task
def google_sheet_synchronization():
    google_task_online()
