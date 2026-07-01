from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# Счётчик запросов — метрика типа Counter
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests to the app"
)

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()  # увеличиваем счётчик при каждом запросе
    return {"message": "Привет!."}

@app.get("/metrics")
def metrics():
    # Эндпоинт который Prometheus будет опрашивать (scrape)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)