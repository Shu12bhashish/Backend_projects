from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["path", "status"]
)

webhook_requests_total = Counter(
    "webhook_requests_total",
    "Webhook processing results",
    ["result"]
)

request_latency_ms = Histogram(
    "request_latency_ms",
    "Request latency in milliseconds",
    buckets=[100, 500, 1000, float("inf")]
)
