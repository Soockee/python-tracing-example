#!/usr/bin/env python


from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.propagate import extract
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.wsgi import collect_request_attributes

from numpy import random
from time import sleep

from flask import jsonify, request
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
RequestsInstrumentor().instrument()

@app.route("/")
def entry():
        sleeptime = random.uniform(1, 7)
        with tracer.start_as_current_span("sleeper_receiver",context=extract(request.headers), kind=trace.SpanKind.SERVER, attributes=collect_request_attributes(request.environ)) as span:
            span.set_attribute("is_example", "yes :) hehe")
            sleep(sleeptime)
        return jsonify(msg="Hello From Receiver")


app.run(debug=True, host='0.0.0.0', port=8080)