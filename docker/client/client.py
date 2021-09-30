import requests
import sys
import time
from opentracing.ext import tags
from opentracing.propagation import Format
import logging
from jaeger_client import Config
import http.server

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

class MyHttpRequestHandler():
    def http_get():
        # Create span with a unique name
        with tracer.start_span('my_super_cool_request') as span:
            url = 'http://server'

            headers = {}
            # Add headers to the tracer
            tracer.inject(span, Format.HTTP_HEADERS, headers)

            # Add a custom event
            span.log_kv({'event': 'sent request'})

            # For debug purpose
            print(headers)

            # Hit the server
            r = requests.get(url, headers=headers)

            # Check if we have a 200 response
            assert r.status_code == 200

            # Another random event
            span.log_kv({'event': 'return response'})
            return r.text


# Init tracer
tracer = init_tracer('client')

print('Client is running')

# Main function
getIt = MyHttpRequestHandler
print(getIt.http_get())

# Wait before closing
time.sleep(2)
tracer.close()
