#!/usr/bin/env python

# Traces
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.propagate import inject
# Metrics
#from opentelemetry import metrics
#from opentelemetry.sdk.metrics.export.controller import PushController
#from opentelemetry.sdk.metrics import MeterProvider
#from opentelemetry.exporter.prometheus import PrometheusMetricsExporter

# other stuff 
from numpy import random
from time import sleep

import flask
import requests




# Configure the tracer to export traces to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
# Configure the tracer using the default implementation
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(jaeger_exporter)
)    
# Application code uses an OpenTelemetry Tracer as usual.
tracer = trace.get_tracer(__name__)

# init flask app 
app = flask.Flask(__name__)
FlaskInstrumentor().instrument_app(app)



#start_http_server(port=9000, addr="prometheus")
#meter = metrics.get_meter(__name__)
#exporter = PrometheusMetricsExporter("Sender")
#controller = PushController(meter, exporter, 5)
#metrics.get_meter_provider().start_pipeline(meter, exporter, 1)



requests_count = 0

#counter = meter.create_observable_up_down_counter(
    #name="requests",
    #description="number of requests",
    #callback= lambda result: result.Observe(requests_count),
#)

@app.route("/")
def entry():
    sleeptime = random.uniform(1, 2)
    # internal host:port
    receiver_url = "http://receiver:8080"
    with tracer.start_as_current_span("Sleeper") as span:
        span.set_attribute("is_example", "yes :)")
        headers = {}
        inject(headers)
        # pretend to do work
        sleep(sleeptime)
        # downstream service call
        response = requests.get(receiver_url, headers=headers).json()
        # return response
    
    return response if response is not None else ("error while GET " + receiver_url)


app.run(debug=True, host='0.0.0.0',port=8080)