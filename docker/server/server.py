import http.server
import socketserver
import logging
from urllib.parse import urlparse
from urllib.parse import parse_qs
from jaeger_client import Config
import time
from opentracing.ext import tags
from opentracing.propagation import Format
from random import randrange

# Tracer init and config
def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': "my-jaeger-agent.observability.svc.cluster.local",
            },
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name= service
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()   

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract informations for Jaeger
        span_ctx = tracer.extract(Format.HTTP_HEADERS, self.headers)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
        with tracer.start_span('format', child_of=span_ctx, tags=span_tags) as span:

            # Sending an '200 OK' response
            self.send_response(200)

            # Setting the header
            self.send_header("Content-type", "text/html")

            # Whenever using 'send_header', you also have to call 'end_headers'
            self.end_headers()

            # Forge html response
            html = f"<html><head></head><body><h1>Hello</h1></body></html>"

            span.log_kv({'event': 'this is a span'})

            # Add some random latency
            time.sleep(randrange(5))

            # Writing the HTML contents with UTF-8
            self.wfile.write(bytes(html, "utf8"))
            return

# Init tracer
tracer = init_tracer('server')

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 80

# Configure the server
my_server = socketserver.TCPServer(("0.0.0.0", PORT), handler_object)

print('Backend server is running')

# Start the server
my_server.serve_forever()
