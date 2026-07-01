# Module 15 — Observability: Prometheus, Grafana, ServiceMonitor

Observability (наблюдаемость) — способность понять что происходит внутри системы по её внешним сигналам. Стоит на трёх столпах:

**Metrics (Метрики)** — числовые показатели во времени: CPU 80%, память 2ГБ, 150 запросов/сек, латентность 200мс. Агрегированные цифры для графиков и алертов. Отвечают на вопрос **"что происходит?"**. Инструменты: Prometheus (собирает), Grafana (рисует).

**Logs (Логи)** — записи о конкретных событиях с временной меткой: `14:32:01 User logged in`, `14:32:05 ERROR: database connection failed`. Дискретные текстовые события. Отвечают на вопрос **"почему это случилось?"**. Инструменты: Loki, ELK (Elasticsearch).

**Traces (Трейсы)** — путь одного запроса через всю систему микросервисов: запрос → сервис A (10мс) → сервис B (5мс) → база (200мс, вот затык) → ответ. Отвечают на вопрос **"где именно проблема?"** в цепочке. Инструменты: Jaeger, Zipkin.

## Установка Prometheus Stack через Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

Одной командой развернулись Prometheus, Grafana, Alertmanager, node-exporter, kube-state-metrics и набор готовых дашбордов.

```bash
kubectl get pods -n monitoring
```

```
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          8m
prometheus-grafana-9cdf49dd4-kz6b4                       3/3     Running   0          9m
prometheus-kube-prometheus-operator-...                  1/1     Running   0          9m
prometheus-kube-state-metrics-...                        1/1     Running   0          9m
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          8m
prometheus-prometheus-node-exporter-...                  1/1     Running   0          9m
```

## Доступ к Prometheus UI

```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 --address=0.0.0.0 &
```

Открывается на `http://localhost:9090`. Запрос `up` в поле Query показывает все опрашиваемые targets кластера (значение 1 = target жив).

## Доступ к Grafana

Получить пароль admin:

```bash
kubectl --namespace monitoring get secrets prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 --address=0.0.0.0 &
```

Открывается на `http://localhost:3000` логин `admin`, пароль из команды выше.

## Готовые дашборды

kube-prometheus-stack автоматически установил десятки дашбордов. Дашборд **Kubernetes / Compute Resources / Cluster** показывает реальные метрики кластера:

```
CPU Utilisation:            2.19%
CPU Requests Commitment:    7.92%
Memory Utilisation:         20.6%
```

Плюс разбивка по namespace (monitoring, ingress-nginx, kube-system) — сколько подов, workloads, CPU и памяти запрошено.

## ServiceMonitor — как Prometheus находит сервисы

Prometheus в K8s не требует ручного прописывания IP подов. Он автоматически ищет объекты `kind: ServiceMonitor`, которые описывают кого опрашивать (scrape) через label selector. Когда поды пересоздаются с новыми IP — Prometheus сам подхватывает новые.

## Метрики из приложения

В `app.py` добавлена библиотека `prometheus-client` и эндпоинт `/metrics`:

```python
from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests to the app"
)

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    return {"message": "Привет!."}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

В `requirements.txt` добавлен `prometheus-client`.

Проверка после пересборки и деплоя:

```bash
kubectl port-forward pod/my-app-deployment-... 5000:5000 &
curl http://localhost:5000/metrics | grep app_requests_total
```

```
# HELP app_requests_total Total number of requests to the app
# TYPE app_requests_total counter
app_requests_total 2.0
```

Счётчик растёт с каждым запросом к `/`.

## app-service.yml

Для ServiceMonitor порт сервиса должен иметь имя (`http`), а сам сервис — label для поиска:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  labels:
    app: my-app
spec:
  selector:
    app: my-app
  ports:
    - name: http
      port: 80
      targetPort: 5000
  type: NodePort
```

## app-monitor.yml

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: http
      path: /metrics
```

Ключевой момент — `labels: release: prometheus`. Prometheus из kube-prometheus-stack по умолчанию находит только ServiceMonitor'ы с этим label.

```bash
kubectl apply -f app-monitor.yml
```

## Проверка Targets

Через 1-2 минуты в Prometheus UI → Status → Target health появляется `serviceMonitor/default/my-app-monitor`:

```
serviceMonitor/default/my-app-monitor/0     3/3 up

http://10.244.0.25:5000/metrics   UP
http://10.244.0.26:5000/metrics   UP
http://10.244.0.27:5000/metrics   UP
```

Prometheus сам обнаружил все 3 пода через label selector и начал собирать `/metrics` — без ручного прописывания IP.

## Логи

Просмотр логов всего Deployment:

```bash
kubectl logs deployment/my-app-deployment
```

```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     10.244.0.24:49222 - "GET /metrics HTTP/1.1" 200 OK
INFO:     10.244.0.24:55542 - "GET /metrics HTTP/1.1" 200 OK
```

Streaming логов в реальном времени (выход по Ctrl+C):

```bash
kubectl logs -f deployment/my-app-deployment
```

В логах видно как Prometheus (IP `10.244.0.24`) каждые ~30 секунд опрашивает `/metrics` и получает `200 OK` — живое подтверждение что ServiceMonitor работает.