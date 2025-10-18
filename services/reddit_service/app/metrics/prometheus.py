# app/metrics/prometheus.py
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

REDDIT_REQUESTS_TOTAL = Counter(
    "reddit_requests_total",
    "Total number of requests to Reddit API",
    ["subreddit", "mode"]
)

REDDIT_REQUEST_DURATION = Histogram(
    "reddit_request_duration_seconds",
    "Duration of Reddit API requests",
    ["subreddit", "mode"]
)

def init_metrics(app):
    """Initialize Prometheus metrics"""
    Instrumentator().instrument(app).expose(app)