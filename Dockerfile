FROM python:3.11
WORKDIR /repo

RUN python3 -m pip install --upgrade pip wheel setuptools
COPY requirements.txt .
RUN pip install -r requirements.txt --default-timeout=10000 --src /usr/local/src
COPY setup.py .
RUN pip install -e .

# CMD ["celery", "-A", "worker", "worker", "--loglevel=INFO", "--pidfile=/tmp/dc_orchestra.pid", "--logfile=/root/dc_orchestra.log", "--concurrency=4", "--queues=dc_orchestra_q", "--hostname=docker_localhost_orchestra"]

# CMD ["python", "-m", "http.server"]
CMD ["celery", "-A", "Orchestrator.worker", "worker"]