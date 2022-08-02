import os

from flasgger import Swagger
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from redis import Redis

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

SWAGGER_TEMPLATE = {
    "securityDefinitions": {
        "session_token": {
            "type": "apiKey", "name": "Authorization", "in": "header"
        }
    }
}

app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_CONFIG')
                       or 'config.DevelopmentConfig')


db = SQLAlchemy(app)
db.init_app(app)
jwt = JWTManager(app)
swagger = Swagger(app, template=SWAGGER_TEMPLATE)
mail = Mail(app)
redis = Redis(host=os.getenv("REDIS_HOST") or "0.0.0.0")


@app.before_request
def before_request():
    if os.getenv("FLASK_CONFIG", False) == "config.ProductionConfig":
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=os.getenv("JAEGER_AGENT_HOST", 'localhost'),
                agent_port=int(os.getenv("JAEGER_AGENT_PORT", 6831)),
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()
FlaskInstrumentor().instrument_app(app)
