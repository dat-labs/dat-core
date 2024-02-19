"""
Entry point module for dat pipeline worker
"""
import os
from subprocess import call
from celery import Celery

app = Celery(broker='amqp://mq_user:mq_pass@message-queue:5672//')


@app.task(queue='dat-worker-q', name='dat_worker_task')
def worker(connection_obj):
    '''celery worker
    Args:
        orchestra_id (int): dc_admin.orchestrations.id
        run_type (str): MANUAL or SCHEDULED
        m_user (str): machine username to impersonate which needs to run the script
    '''
    _cmd = ''
    print(_cmd)
    call(_cmd.split(' '))

if False:
    app.send_task('dat_worker_q', (connection_obj, ), queue='dat-worker-q')
    