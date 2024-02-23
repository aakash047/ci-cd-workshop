from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge
import time
import random
import threading
import time

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

by_path_counter = Counter('by_path_counter', 'Request count by request paths', ['path'])
latency_gauge = Gauge('request_latency_seconds_rate','Rate of request latency in seconds',['path', 'le'])

counter_lock = threading.Lock()  # Lock for thread safety
counter = 0 
le_values = [0.5, 1.0, 1.5, 2.0, 100.0]
url1_dict = {key: 0 for key in le_values}
url2_dict = {key: 0 for key in le_values}

def reset_counter():
    global counter
    global le_values
    global url1_dict
    global url2_dict
    while True:
        time.sleep(15)  # Reset the counter every 60 seconds
        with counter_lock:
            counter = 0  # Reset the counter value
            for le in le_values:
                count_1 = url1_dict.get(le)
                count_2 = url2_dict.get(le)
                print(count_1, le, 'url1')
                print(count_2, le, 'url2')
                latency_gauge.labels(path='/url1', le=le).set(count_1)
                latency_gauge.labels(path='/url2', le=le).set(count_2)
            url1_dict = {key: 0 for key in url1_dict}
            url2_dict = {key: 0 for key in url2_dict}

def increment_counter():
    global counter
    while True:
        with counter_lock:
            counter += 1  # Increment the counter value
            print("Counter value: {}".format(counter))
        time.sleep(1)  # Increment the counter every 1 second


# Create a thread for the reset_counter function
reset_counter_thread = threading.Thread(target=reset_counter)

# Create a thread for the increment_counter function
increment_counter_thread = threading.Thread(target=increment_counter)

# Start the reset_counter and increment_counter threads
reset_counter_thread.start()
increment_counter_thread.start()

@app.route('/url1')
@metrics.do_not_track()
def url1_get():
    global counter
    global le_values
    global url1_dict
    request_number = by_path_counter.labels(path='/url1')._value.get() % 10
    if request_number == 9:  # 10th request
        latency = random.uniform(50, 100)  
    else:
        latency = random.uniform(0, 2)  

    by_path_counter.labels(path='/url1').inc()

    if counter != 15:
        url1_dict = {key: value + 1 if latency < key else value for key, value in url1_dict.items()}

    return {
        'status': '200'
    }

@app.route('/url2')
@metrics.do_not_track()
def url2_get():
    global counter
    global le_values
    global url2_dict
    request_number = by_path_counter.labels(path='/url2')._value.get() % 10
    if request_number == 9:  # 10th request
        latency = random.uniform(50, 100)  
    else:
        latency = random.uniform(0, 2)  

    by_path_counter.labels(path='/url2').inc()

    if counter != 15:
        url2_dict = {key: value + 1 if latency < key else value for key, value in url2_dict.items()}

    return {
        'status': '200'
    }

@app.route('/url3')
def url3_get():
    return {
        'status': '200',
        'message': 'Hello World'
    }

app.run(host='0.0.0.0', port=5001)
