FROM python:3.11.8-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "python3", "flask_prometheus.py" ]
