"""
Metrics collection for the application.
"""
import time
from prometheus_client import Counter, Histogram, Gauge, Info

# Initialize metrics
MODEL_INFO = Info('ansible_llm_model', 'Information about the loaded model')

REQUEST_COUNT = Counter(
    'ansible_llm_requests_total', 
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'ansible_llm_request_latency_seconds', 
    'Request latency in seconds',
    ['method', 'endpoint']
)

MODEL_INFERENCE_LATENCY = Histogram(
    'ansible_llm_model_inference_latency_seconds', 
    'Model inference latency in seconds',
    ['model_name']
)

ACTIVE_REQUESTS = Gauge(
    'ansible_llm_active_requests', 
    'Number of active requests',
    ['method', 'endpoint']
)

def init_model_metrics(model_name, model_size, quantization):
    """Initialize model information metrics."""
    MODEL_INFO.info({
        'name': model_name,
        'size': str(model_size),
        'quantization': str(quantization) if quantization else 'none'
    })

class RequestLatencyMiddleware:
    """Middleware to track request latency and counts."""
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
        
        try:
            response = await call_next(request)
            status = response.status_code
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            raise e
        finally:
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
