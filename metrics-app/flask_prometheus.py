from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Histogram, Counter
import time
import random

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

latency_histogram = Histogram('request_latency_seconds', 'Request latency in seconds', ['path'], buckets=[0.5, 1, 1.5, 2.0, 100.0])
by_path_counter = Counter('by_path_counter', 'Request count by request paths', ['path'])

@app.route('/url1')
@metrics.do_not_track()
def url1_get():
    request_number = by_path_counter.labels(path='/url1')._value.get() % 10
    if request_number == 9:  # 10th request
        latency = random.uniform(50, 100)  
    else:
        latency = random.uniform(0, 2)  

    # time.sleep(latency)
    latency_histogram.labels(path='/url1').observe(latency)
    by_path_counter.labels(path='/url1').inc()

    return {
        'status': '200'
    }

@app.route('/url2')
@metrics.do_not_track()
def url2_get():
    request_number = by_path_counter.labels(path='/url2')._value.get() % 10
    if request_number == 9:  # 10th request
        latency = random.uniform(50, 100)  
    else:
        latency = random.uniform(0, 2)  

    # time.sleep(latency)
    latency_histogram.labels(path='/url2').observe(latency)
    by_path_counter.labels(path='/url2').inc()

    return {
        'status': '200'
    }

@app.route('/url3')
def url3_get():
    return {
        'status': 'Hello World'
    }

app.run(host='0.0.0.0', port=5001)