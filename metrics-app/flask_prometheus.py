from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

by_path_counter = metrics.counter(
    'by_path_counter', 'Request count by request paths',
    labels={'path': lambda: request.path}
)


@app.route('/url1')
@metrics.do_not_track()
@by_path_counter
def simple_get():
    return {
        'status': '200'
    }


@app.route('/url1')
@metrics.do_not_track()
@by_path_counter
def url1_get():
    return {
        'status': '200'
    }


@app.route('/url3')
@metrics.do_not_track()
@by_path_counter
def url2_get():
    return {
        'status': '200'
    }


app.run(host='0.0.0.0', port=5001)
