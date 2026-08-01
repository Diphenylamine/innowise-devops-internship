# nginx vs Caddy vs Traefik - Load Balancer Comparison
## Что такое Load Balancer

**Балансировщик нагрузки** - компонент, который принимает входящий трафик и распределяет его между несколькими одинаковыми экземплярами (репликами) приложения, вместо того чтобы весь трафик шёл на один сервер.

**Зачем он нужен:**
- **Масштабируемость** - одно приложение физически не выдержит весь трафик в одиночку, нагрузка размазывается между всеми репликами
- **Отказоустойчивость** - если одна реплика падает, балансировщик перестаёт направлять на неё трафик, остальные продолжают работать
- **Zero-downtime deploy** - можно обновлять реплики по одной, не останавливая сервис целиком

**Базовые алгоритмы распределения трафика:**
- **Round-robin** - по очереди, один за другим (реплика 1 → 2 → 3 → 1 → 2 → 3...)
- **Least connections** - на ту реплику, у которой сейчас меньше всего активных соединений
- **IP hash** - клиент с одним и тем же IP всегда попадает на одну и ту же реплику (полезно для сессий)

Для тестов везде используется одно и то же приложение - простенький FastAPI-сервис со страничкой (там ещё крутящийся кубик) и кнопкой, а под капотом эндпоинт `/api/server-number`, который при старте процесса один раз кидает рандомное число и потом всегда отдаёт его же. Удобно - по числу сразу видно, какая именно реплика ответила.

---

## Архитектура - как каждый из трёх устроен внутри

Прежде чем переходить к практике, нужно изучмит как устроен каждый инструмент - чтобы понимать, чего вообще ожидать от балансировки, ещё до первого теста.

### nginx

nginx устроен по классической схеме "мастер и рабочие". Master-процесс ничего не обрабатывает сам - он только читает конфиг, биндит порты и управляет воркерами. Вся реальная работа (обработка соединений, чтение с диска, общение с бэкендами) происходит в worker-процессах.

Официальный блог nginx описывает это так:

> "The master process performs the privileged operations such as reading configuration and binding to ports, and then creates a small number of child processes... The worker processes do all of the work! They handle network connections, read and write content to disk, and communicate with upstream servers."

Каждый воркер однопоточный, но благодаря событийной неблокирующей модели один воркер спокойно держит тысячи соединений одновременно. Число воркеров задаётся через `worker_processes` (по умолчанию можно поставить `auto` - тогда nginx сам берёт число ядер CPU):

> "In most cases, the recommended NGINX configuration of one worker process per CPU core makes the most efficient use of hardware resources."

То есть, если где-то будет несколько воркеров вместо одного - это будут независимые процессы с отдельными счётчиками (на это стоит обратить внимание при тестировании балансировки).

Официальная документация также прямо указывает, какой алгоритм балансировки используется по умолчанию:

> "When the load balancing method is not specifically configured, it defaults to round-robin."

То есть будет строгий циклический порядок `1→2→3→1→2→3`, если явно не переопределять метод.

Ещё интересный момент - что происходит при `nginx -s reload`:

> "When the master process receives a SIGHUP, it reloads the configuration and forks a new set of worker processes... signals the old worker processes to gracefully exit."

То есть reload - это не "на лету поменять параметры" у старых процессов, а честно поднять новые воркеры с новым конфигом, и только когда они готовы - аккуратно убить старые.

### Caddy

У Caddy принципиально другая философия. Это не "master + воркеры", а гибкая система модулей, где буквально всё - HTTP-обработчики, TLS-сертификаты, хранилища - это отдельные подключаемые модули:

> "Caddy's architecture is built around a powerful module system. Every piece of functionality - from HTTP handlers and matchers to TLS issuers and certificate storage backends - is implemented as a module."

Ещё любопытный факт, который стоит держать в голове перед конфигурацией балансировки - `Caddyfile`, с которым предстоит работать, вообще не является "родным" языком Caddy. Внутри себя Caddy думает исключительно в JSON, а `Caddyfile` - это просто удобная надстройка для людей:

> "The format of the config document takes many forms with config adapters, but Caddy's native config language is JSON."

И именно поэтому у Caddy нет команды в духе `nginx -s reload` - вместо этого конфигурация меняется через живой **Admin API**, прямо во время работы процесса:

> "Configuration is both dynamic and exportable with Caddy's API... Changing a running server's active configuration (often called a 'reload') can be tricky with high levels of concurrency... Caddy solves this problem elegantly."

По балансировке документация `reverse_proxy` заранее предупреждает, какое поведение будет по умолчанию:

> "This is enabled by default, with the random policy."

То есть, в отличие от nginx, получится не строгий цикл, а случайный выбор бэкенда - если явно не указать `lb_policy round_robin`.

### Traefik - EntryPoints, Routers, Middlewares, Services, Providers

У Traefik своя терминология:

> "EntryPoints are the network entry points into Traefik. They define the port which will receive the packets, and whether to listen for TCP or UDP. Routers are in charge of connecting incoming requests to the services that can handle them. Middlewares can modify the requests or responses before they are sent to your service. Services are responsible for configuring how to reach the actual services."

Но самое главное - это **Providers**. Это то, что реально отличает Traefik от двух других инструментов:

> "Traefik is able to use your cluster API to discover the services and read the attached information. In Traefik, these connectors are called providers because they provide the configuration to Traefik."

И вот прямое подтверждение той самой "динамичности" Traefik, ради которой его вообще стоит рассматривать отдельно от nginx и Caddy:

> "When a service is deployed, Traefik detects it immediately and updates the routing rules in real time. Similarly, when a service is removed from the infrastructure, the corresponding route is deleted accordingly. You no longer need to create and synchronize configuration files cluttered with IP addresses or other rules."

Providers у Traefik бывают 4 типов: label-based (Docker labels на контейнерах), key-value-based (Consul/etcd), annotation-based (Kubernetes) и обычный статический файл. В сценариях `outside-docker` и `inside-docker` будет использоваться именно файловый provider - то есть тестировать Traefik в том же статичном режиме, что nginx и Caddy, а не его фирменную способность автоматически находить новые контейнеры. Его основная фича будет только в Kubernetes-сценарии, где он будет работать через Kubernetes provider и свой собственный ресурс `IngressRoute`.

По алгоритму балансировки документация заранее описывает дефолтную стратегию `wrr`:

> "The default strategy. Distributes requests evenly across all servers in rotation, respecting server weights. This strategy uses Earliest Deadline First (EDF) scheduling to provide weighted round-robin behavior."

Значит ожижается не такой простой циклический порядок, как у nginx - EDF-планирование честно распределяет нагрузку в среднем, но не гарантирует строгую последовательность отдельных запросов.

---

# nginx

Официальная документация: [nginx.org/en/docs/http/load_balancing.html](https://nginx.org/en/docs/http/load_balancing.html)

## Что такое nginx

nginx - веб-сервер и обратный прокси (reverse proxy), созданный в 2004 году, известен высокой производительностью и низким потреблением ресурсов. Помимо отдачи статики, умеет работать как:
- Reverse proxy - принимает запрос и перенаправляет на другой сервер
- Load balancer - распределяет запросы между несколькими бэкендами через блок `upstream`
- Ingress Controller в Kubernetes - тот же nginx, но управляемый через K8s API вместо ручного конфига

**Философия конфигурации nginx: полностью ручная и статическая.** Список бэкендов прописывается явно в конфиг-файле, при изменении списка (новая реплика, удалённая реплика) конфиг нужно переписать и перечитать (`nginx -s reload`).

---

## Сценарий 1: nginx вне Docker (прямо на хосте)

nginx стоит прямо на хосте (в WSL), а три реплики приложения крутятся в Docker с портами, проброшенными наружу. nginx на хосте про Docker вообще ничего не знает - он просто стучится на `127.0.0.1` в три разных порта, как будто это три обычных сервера.

### docker-compose.yml (только бэкенды, без nginx - он снаружи)

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    ports:
      - "5001:5000"

  app2:
    build: ../app
    hostname: app2
    ports:
      - "5002:5000"

  app3:
    build: ../app
    hostname: app3
    ports:
      - "5003:5000"
```

### Конфиг nginx (`/etc/nginx/nginx.conf`)

```nginx
events {}

http {
    upstream backend {
        server 127.0.0.1:5001;
        server 127.0.0.1:5002;
        server 127.0.0.1:5003;
    }

    server {
        listen 8081;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

Бэкенды прописаны как реальные порты хоста (`127.0.0.1:5001` и так далее) - три адреса, как будто три соседних сервера.

### Проверка конфига

```bash
sudo nginx -t
sudo systemctl reload nginx
```

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Тест

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8081/api/server-number; echo; done
```

```
{"number":98}
{"number":757}
{"number":129}
{"number":98}
{"number":757}
{"number":129}
```

Три числа чётко чередуются по кругу - ровно то поведение, что и описано в разделе "Архитектура" (round-robin по умолчанию).

### Проверка количества воркеров у nginx

```bash
ps aux | grep "nginx: worker"
```

```
nobody      2449  0.0  0.0  12788  4504 ?        S    23:38   0:00 nginx: worker process
```

Всего один. Именно поэтому порядок такой строгий и предсказуемый - один процесс держит один общий счётчик "чья сейчас очередь", и никто ему не мешает.

---

## Сценарий 2: nginx внутри Docker

Сам nginx запускается как отдельный контейнер в той же docker-сети, что и три реплики приложения. К бэкендам он обращается по Docker DNS-именам, а не по портам хоста.

### docker-compose.yml (полный, nginx тоже как сервис)

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    expose:
      - "5000"
  app2:
    build: ../app
    hostname: app2
    expose:
      - "5000"
  app3:
    build: ../app
    hostname: app3
    expose:
      - "5000"
  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./inside-docker-nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app1
      - app2
      - app3
```

### inside-docker-nginx.conf

```nginx
events {}

http {
    upstream backend {
        server app1:5000;
        server app2:5000;
        server app3:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

Главное отличие от первого сценария: вместо `127.0.0.1:порт` тут просто имена - `app1`, `app2`, `app3`. Docker Compose сам поднимает внутреннюю сеть со своим DNS, и имя сервиса всегда резолвится в актуальный IP контейнера, даже если контейнер пересоздался и получил новый адрес.

### Запуск

```bash
docker-compose up -d --build
```

```
[+] up 7/7
 ✔ Container inside-docker-app1-1  Started
 ✔ Container inside-docker-app2-1  Started
 ✔ Container inside-docker-app3-1  Started
 ✔ Container inside-docker-nginx-1 Started
```

### Тест

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8080/api/server-number; echo; done
```

```
{"number":357}
{"number":121}
{"number":810}
{"number":357}
{"number":121}
{"number":810}
```

Опять тот же самый строгий round-robin, как и ожидалось.

### Проверка логов контейнеров

Ещё один способ проверить честность - проанить логи uvicorn внутри каждого контейнера и увидеть, что запросы туда реально доходили.

```bash
docker logs nginx-app1-1
docker logs nginx-app2-1
docker logs nginx-app3-1
```

**app1:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     172.20.0.5:56686 - "GET / HTTP/1.1" 200 OK
INFO:     172.20.0.5:49600 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:49600 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:49600 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:49600 - "GET /style.css HTTP/1.1" 200 OK
INFO:     172.20.0.5:49600 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:52396 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     127.0.0.1:42134 - "GET /api/server-number HTTP/1.1" 200 OK
```

**app2:**
```
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     172.20.0.5:49156 - "GET /style.css HTTP/1.1" 200 OK
INFO:     172.20.0.5:49642 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:49642 - "GET /favicon.ico HTTP/1.1" 404 Not Found
INFO:     172.20.0.5:49642 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:48342 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     127.0.0.1:42516 - "GET /api/server-number HTTP/1.1" 200 OK
```

**app3:**
```
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     172.20.0.5:35482 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:35482 - "GET /favicon.ico HTTP/1.1" 404 Not Found
INFO:     172.20.0.5:58828 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     172.20.0.5:50578 - "GET /api/server-number HTTP/1.1" 200 OK
INFO:     127.0.0.1:41262 - "GET /api/server-number HTTP/1.1" 200 OK
```

Во всех трёх логах запросы идут с одного и того же IP - `172.20.0.5`. Это адрес самого nginx-контейнера внутри docker-сети. Все три реплики реально получали запросы именно от балансировщика. Запросы с `127.0.0.1` - это собственные проверки через `docker exec`, в обход nginx. `GET /favicon.ico 404` - браузер сам просит иконку сайта, её просто нет, не баг.

### Проверка честности через exec в контейнеры

```bash
docker exec nginx-app1-1 python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/server-number').read())"
```

```
b'{"number":898}'
```

Пять раз подряд - то же самое число. Проверил и `app2` (`814`), и `app3` (`650`) - сопоставление с round-robin последовательностью сходится идеально.

---

## Сценарий 3: nginx внутри Kubernetes (Ingress Controller)

nginx используется как Ingress Controller - тот же движок nginx под капотом, но управляемый декларативно через Kubernetes API.

### Манифесты

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lb-demo-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lb-demo
  template:
    metadata:
      labels:
        app: lb-demo
    spec:
      containers:
        - name: lb-demo
          image: lb-demo-app:k8s
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: lb-demo-service
spec:
  selector:
    app: lb-demo
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: lb-demo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: lb-demo-service
                port:
                  number: 80
```

### Сборка и применение

```bash
eval $(minikube docker-env)
docker build -t lb-demo-app:k8s .
kubectl apply -f app-deployment.yml
kubectl apply -f app-service.yml
kubectl apply -f app-ingress.yml
```

```bash
kubectl get pods -l app=lb-demo
```

```
NAME                                  READY   STATUS    RESTARTS   AGE
lb-demo-deployment-6b4ff55989-gr9sp   1/1     Running   0          33s
lb-demo-deployment-6b4ff55989-jmhhx   1/1     Running   0          33s
lb-demo-deployment-6b4ff55989-tn2f7   1/1     Running   0          33s
```

### Тестирование через  Ingress Controller

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8090:80 --address=0.0.0.0 &
for i in 1 2 3 4 5 6; do curl -s http://localhost:8090/api/server-number; echo; done
```

```
{"number":442}
{"number":833}
{"number":442}
{"number":368}
{"number":442}
{"number":368}
```

### Почему в Kubernetes ответы шли не по порядку

В отличие от первых двух сценариев, тут балансировка какая-то кривая - не тот строгий round-robin, который был раньше. Раз nginx по документации использует `worker_processes` и рекомендует один воркер на ядро CPU, логично предположить, что дело именно в их количестве.

Сначала надо проверить сколько ядер видит нода:

```bash
kubectl exec -n ingress-nginx <pod> -- nproc
```

```
12
```

Потом посмотрел сколько реально воркеров запущено у самого nginx внутри Ingress Controller:

```bash
kubectl exec -n ingress-nginx <pod> -- ps aux | grep "nginx: worker"
```

```
431 www-data  0:00 nginx: worker process
432 www-data  0:00 nginx: worker process
...
(всего 12 строк)
```

Ровно 12 воркеров, один в один по числу ядер. Вот ответ: у каждого воркера свой отдельный процесс со своей собственной памятью, а значит и свой собственный счётчик "чья сейчас очередь". Они друг с другом никак не синхронизируются. Шесть запросов подряд просто по-разному раскидались между этими 12 независимыми воркерами - каждый честно крутит свой цикл 1→2→3, но общей картины идеального порядка из этого не складывается.

Проверили ещё раз колличество воркеров у домашнего host-nginx - там был всего один воркер, несмотря на те же самые 12 ядер на машине. Дело не в железе, а в том что в конфиге не прописан `worker_processes`, и он взял значение по умолчанию (единица), тогда как production Ingress Controller явно настроен на `auto` - именно так, как и рекомендует документация.

**Вывод:** балансировка в K8s работает нормально и в целом честно размазывает нагрузку между репликами, просто из-за нескольких параллельных воркеров отдельные запросы подряд могут не показывать идеально строгий порядок - в отличие от простых однопроцессных конфигов в первых двух сценариях.

Сам алгоритм балансировки как был, так и остался Round Robin - Kubernetes/ingress-nginx не подменяет его на что-то другое по умолчанию. Просто он выполняется параллельно в 12 независимых копиях (по числу воркеров), и со стороны это выглядит как "не по порядку". При желании алгоритм можно явно поменять через аннотацию `nginx.ingress.kubernetes.io/load-balance` (варианты: round_robin, least_conn, ip_hash, ewma).

---

# Caddy

Официальная документация: [caddyserver.com/docs](https://caddyserver.com/docs/)

## Что такое Caddy

Caddy - веб-сервер и обратный прокси, появившийся заметно позже nginx (в 2015 году), написан на Go. Его главная фишка - автоматический HTTPS: Caddy сам получает и обновляет TLS-сертификаты через Let's Encrypt, без единой ручной настройки. Конфиг называется `Caddyfile` и по синтаксису куда компактнее, чем у nginx.

Устроен Caddy иначе, чем nginx - это не master-процесс с воркерами, а модульная система, где каждый кусок функциональности - отдельный подключаемый модуль. Это же объясняет, почему у Caddy нет команды в духе `nginx -s reload` - конфигурация меняется через живой Admin API прямо во время работы.

---

## Сценарий 1: Caddy вне Docker (на хосте)
### Установка

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

```
Setting up caddy (2.6.2-6ubuntu0.24.04.3) ...
```

### docker-compose.yml (только бэкенды)

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    ports:
      - "6001:5000"
  app2:
    build: ../app
    hostname: app2
    ports:
      - "6002:5000"
  app3:
    build: ../app
    hostname: app3
    ports:
      - "6003:5000"
```

Запуск с явным именем проекта через `-p` - чтобы две разные папки `outside-docker` для nginx и Caddy назывались одинаково, и Docker Compose путал их между собой:

```bash
docker-compose -p caddy-outside-docker up -d --build
```

### Caddyfile - с имользование random

```
:8082 {
    reverse_proxy 127.0.0.1:6001 127.0.0.1:6002 127.0.0.1:6003
}
```

```bash
sudo caddy run --config /path/to/outside-docker/Caddyfile
```

### Первый тест

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8082/api/server-number; echo; done
```

```
{"number":593}
{"number":593}
{"number":278}
{"number":398}
{"number":593}
{"number":593}
```

Никакого чёткого цикла - и это ровно то, что написано в документации (см. "Архитектура"): у Caddy `lb_policy` по умолчанию - `random`, а не `round_robin`. Первый же тест это подтвердил на практике: число 593 выскочило четыре раза из шести, причём дважды подряд.

###  Caddyfile - с имользование round_robin

```
:8082 {
    reverse_proxy 127.0.0.1:6001 127.0.0.1:6002 127.0.0.1:6003 {
        lb_policy round_robin
    }
}
```

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8082/api/server-number; echo; done
```

```
{"number":278}
{"number":593}
{"number":398}
{"number":278}
{"number":593}
{"number":398}
```

Теперь чёткий цикл, точно как у nginx.

Полный список вариантов `lb_policy` из документации: `random` (дефолт), `random_choose`, `round_robin`, `least_conn`, `ip_hash`, `first`, `uri_hash`, `header`, `cookie`.

---

## Сценарий 2: Caddy внутри Docker

Caddy тоже сидит в контейнере, в той же docker-сети что и три реплики приложения. Обращается к бэкендам по Docker DNS-именам.

### docker-compose.yml

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    expose:
      - "5000"
  app2:
    build: ../app
    hostname: app2
    expose:
      - "5000"
  app3:
    build: ../app
    hostname: app3
    expose:
      - "5000"
  caddy:
    image: caddy:alpine
    ports:
      - "8083:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    depends_on:
      - app1
      - app2
      - app3
```

### Caddyfile

```
:80 {
    reverse_proxy app1:5000 app2:5000 app3:5000 {
        lb_policy round_robin
    }
}
```

Сразу указал `round_robin`.

```bash
docker-compose -p caddy-inside-docker up -d --build
```

```
✔ Container caddy-inside-docker-app1-1  Started
✔ Container caddy-inside-docker-app2-1  Started
✔ Container caddy-inside-docker-app3-1  Started
✔ Container caddy-inside-docker-caddy-1 Started
```

### Тест

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8083/api/server-number; echo; done
```

```
{"number":588}
{"number":844}
{"number":411}
{"number":588}
{"number":844}
{"number":411}
```

Строгий round-robin.

### Проверка честности через exec - во все три контейнера

```bash
docker exec caddy-inside-docker-app1-1 python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/server-number').read())"
```

```
b'{"number":411}'
```

Восемь раз подряд - то же самое число каждый раз:

```
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
b'{"number":411}'
```

Проверили `app2`:

```
b'{"number":588}'
b'{"number":588}'
b'{"number":588}'
b'{"number":588}'
```

И `app3`:

```
b'{"number":844}'
b'{"number":844}'
b'{"number":844}'
b'{"number":844}'
b'{"number":844}'
b'{"number":844}'
```

Сопоставил с round-robin последовательностью через Caddy `588 → 844 → 411 → 588 → 844 → 411`:

| Контейнер | Число |
|---|---|
| app1 | 411 |
| app2 | 588 |
| app3 | 844 |

`app2 → app3 → app1 → app2 → app3 → app1` - полное доказательство честной балансировки.

---

## Сценарий 3: Caddy внутри Kubernetes

У Caddy нет такого зрелого официального Ingress Controller'а, как `ingress-nginx`. Сначала попробовал сделать сам, потом нашел официальный

### Попытка 1: ручной ConfigMap + Caddyfile (DIY-подход)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: caddy-config
data:
  Caddyfile: |
    :80 {
        reverse_proxy caddy-demo-service:80 {
            lb_policy round_robin
        }
    }
```

Caddy тут обращается не к трём конкретным подам, а к одному Kubernetes Service.

```bash
kubectl apply -f app-deployment.yml
kubectl apply -f app-service.yml
kubectl apply -f caddy-configmap.yml
kubectl apply -f caddy-deployment.yml
```

### Тест

```bash
kubectl port-forward service/caddy-proxy-service 8091:80 --address=0.0.0.0 &
for i in 1 2 3 4 5 6; do curl -s http://localhost:8091/api/server-number; echo; done
```

```
{"number":529}
{"number":529}
{"number":529}
{"number":529}
{"number":529}
{"number":529}
```

Одно и то же число все шесть раз. Причина здесь чисто в конкретной конфигурации: `lb_policy round_robin` нечего делать, если у Caddy в списке бэкендов ровно один элемент (сам Service). Реальная балансировка между тремя подами происходит внутри самого Service через kube-proxy, но раз соединение keep-alive, оно всё время идёт к одному и тому же поду.

### Попытка 2: настоящий официальный Caddy Ingress Controller

 Официальный проект реально существует - **`caddyserver/ingress`**, в организации самой команды Caddy на GitHub, помечен как "WIP" (work in progress). Устанавливается через Helm, использует стандартный K8s `Ingress` ресурс, сам следит за изменениями через K8s API.

```bash
git clone https://github.com/caddyserver/ingress.git
cd ingress
helm template mycaddy ./charts/caddy-ingress-controller \
  --namespace=caddy-system \
  > mycaddy.yaml
kubectl create namespace caddy-system
kubectl apply -f mycaddy.yaml
```

```
poddisruptionbudget.policy/mycaddy-caddy-ingress-controller created
serviceaccount/caddy-ingress-controller created
configmap/caddy-ingress-controller-configmap created
clusterrole.rbac.authorization.k8s.io/caddy-ingress-controller-role created
clusterrolebinding.rbac.authorization.k8s.io/caddy-ingress-controller-role-binding created
service/mycaddy-caddy-ingress-controller created
deployment.apps/mycaddy-caddy-ingress-controller created
```

### Первая проблема

```bash
kubectl describe pod -n caddy-system <pod-name> | grep -A 5 "Events:"
```

```
Warning  FailedScheduling  116s  default-scheduler  0/1 nodes are available: 1 node(s) didn't have free ports for the requested pod ports.
```

Контроллер использует `hostPort` - каждая реплика напрямую занимает порты 80/443/9765 ноды. Chart по умолчанию ставит 2 реплики, а в Minikube одна нода. Пересобрал с одной репликой, но всё равно `Pending`. в интернете нашел решение, просто переустановить. Попробовал, после этого под Caddy ожил.

### Проверка, что контроллер реально видит наш Ingress

```bash
kubectl logs -n caddy-system -l app.kubernetes.io/name=caddy-ingress-controller --tail=30
```

```
"msg":"Ingress created (default/caddy-real-ingress)"
```

Контроллер сам увидел ресурс через K8s API и перестроил конфигурацию, без единого нашего ручного вмешательства - именно то, чего не умел DIY-подход.

### Вторая проблема - автоматический HTTPS редирект

```bash
curl -v http://localhost:8092/api/server-number
```

```
< HTTP/1.1 308 Permanent Redirect
< Location: https://localhost/api/server-number
< Server: Caddy
```

Автоматический HTTPS - особенность Caddy, только теперь она не нужна и мешает работе. Полез искать как можно отключить. Смотрел исходный код контроллера на GitHub. В `values.yaml` подходящего флага не нашлось, зато в коде обнаружилось:

```go
HTTPServer: {
    AutoHTTPS: &caddyhttp.AutoHTTPSConfig{},   // пустая структура = включено по умолчанию
}
```

Жёстко зашито в коде, не настраивается через Helm values. Но нашлась нужная аннотация именно для отдельного Ingress-ресурса, прямо в исходниках контроллера:

```go
disableSSLRedirect = "disable-ssl-redirect"
```

```yaml
metadata:
  annotations:
    kubernetes.io/ingress.class: caddy
    caddy.ingress.kubernetes.io/disable-ssl-redirect: "true"
```


### Финальный тест - и снова одно и то же число

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8092/api/server-number; echo; done
```

```
{"number":248}
{"number":248}
{"number":248}
{"number":248}
{"number":248}
{"number":248}
```

Даже с официальным контроллером - та же история. Попробовал `Connection: close`, число всё равно не менялось внутри одного прогона. Полезл в документацию `reverse_proxy` (раздел про `http` transport) - этого нюанса в общей архитектуре Caddy заранее не было, узнали только сейчас:

> "keepalive is either off or a duration value that specifies how long to keep connections open. Default: 2m."

Сaddy держит keep-alive соединение к Service по умолчанию 2 минуты. А Kubernetes Service - это, по сути, iptables/conntrack DNAT-правило: когда устанавливается TCP-соединение к ClusterIP, kube-proxy один раз выбирает конкретный под и закрепляет это соединение за ним на весь срок его жизни. Пока Caddy переиспользует один и тот же keep-alive канал - все запросы идут на один и тот же под.

Это не баг и не ошибка конфигурации - а задокументированное поведение технологий, просто их комбинация даёт не совсем то, что интуитивно ожидаешь от "балансировщика перед репликами".

---

# Traefik

Официальная документация: [doc.traefik.io/traefik](https://doc.traefik.io/traefik/)

## Что такое Traefik

Traefik - реверс-прокси и балансировщик на Go, специально заточенный под динамическую инфраструктуру. Ключевое отличие от nginx и Caddy - Traefik не читает статичный конфиг с зашитым списком бэкендов, а сам следит за API оркестратора (Docker, Kubernetes) и обновляет маршруты сам, без перезагрузки, как только появляется или исчезает контейнер.

Конфигурация Traefik разделена на два уровня: static configuration (общие настройки - какие точки входа слушать, какие провайдеры использовать) и dynamic configuration (правила маршрутизации и список бэкендов). У nginx и Caddy всё это было в одном файле.

---

## Сценарий 1: Traefik вне Docker (на хосте)

### Установка

```bash
curl -L https://github.com/traefik/traefik/releases/download/v3.1.2/traefik_v3.1.2_linux_amd64.tar.gz -o traefik.tar.gz
tar -xzf traefik.tar.gz
sudo mv traefik /usr/local/bin/
```

```
Version:      3.1.2
Codename:     comte
```

### docker-compose.yml (только бэкенды)

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    ports:
      - "7001:5000"
  app2:
    build: ../app
    hostname: app2
    ports:
      - "7002:5000"
  app3:
    build: ../app
    hostname: app3
    ports:
      - "7003:5000"
```

```bash
docker-compose -p traefik-outside-docker up -d --build
```

### Статическая конфигурация - traefik.yml

```yaml
entryPoints:
  web:
    address: ":8093"

providers:
  file:
    filename: /path/to/outside-docker/dynamic.yml
```

Тут наступил на грабли - сначала указал путь `/etc/traefik/dynamic.yml`, скопировав идею с того, как это выглядело бы в контейнере. Но раз Traefik работает прямо на хосте, нужен реальный путь на хосте.

### Динамическая конфигурация - dynamic.yml

```yaml
http:
  services:
    backend:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:7001"
          - url: "http://127.0.0.1:7002"
          - url: "http://127.0.0.1:7003"

  routers:
    my-router:
      rule: "PathPrefix(`/`)"
      service: backend
```

### Запуск

```bash
traefik --configFile=/path/to/traefik.yml
```

В отличие от nginx и Caddy, Traefik по умолчанию не пишет вообще никаких логов о старте в консоль. Процесс тихо висит, слушая порт.

### Тест

```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8093/api/server-number; echo; done
```

```
{"number":812}
{"number":775}
{"number":802}
{"number":775}
{"number":802}
{"number":812}
```

Это не строгий цикл вида `A→B→C→A→B→C` - и это как раз согласуется с тем, что было в доккументации: Traefik использует EDF-scheduling, а не наивный циклический счётчик, поэтому строгого порядка можно было не ждать с самого начала. Проверил ещё раз с бОльшим числом запросов для наглядности:

```bash
for i in 1 2 3 4 5 6 7 8 9; do curl -s http://localhost:8093/api/server-number; echo; done
```

```
{"number":802}
{"number":812}
{"number":775}
{"number":812}
{"number":775}
{"number":802}
{"number":775}
{"number":802}
{"number":812}
```

Все три числа встречаются примерно поровну, но без фиксированного цикла из трёх шагов подряд.

---

## Сценарий 2: Traefik внутри Docker

### docker-compose.yml

```yaml
services:
  app1:
    build: ../app
    hostname: app1
    expose:
      - "5000"
  app2:
    build: ../app
    hostname: app2
    expose:
      - "5000"
  app3:
    build: ../app
    hostname: app3
    expose:
      - "5000"
  traefik:
    image: traefik:v3.1
    ports:
      - "8094:80"
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
    depends_on:
      - app1
      - app2
      - app3
```

### traefik.yml

```yaml
entryPoints:
  web:
    address: ":80"

providers:
  file:
    filename: /etc/traefik/dynamic.yml
```

На этот раз путь `/etc/traefik/dynamic.yml` уже правильный - Traefik работает внутри контейнера.

### dynamic.yml

```yaml
http:
  services:
    backend:
      loadBalancer:
        servers:
          - url: "http://app1:5000"
          - url: "http://app2:5000"
          - url: "http://app3:5000"

  routers:
    my-router:
      rule: "PathPrefix(`/`)"
      service: backend
```

```bash
docker-compose -p traefik-inside-docker up -d --build
```

### Тест

```bash
for i in 1 2 3 4 5 6 7 8 9; do curl -s http://localhost:8094/api/server-number; echo; done
```

```
{"number":200}
{"number":722}
{"number":360}
{"number":722}
{"number":360}
{"number":200}
{"number":360}
{"number":200}
{"number":722}
```

Тот же самый характерный паттерн EDF-планирования, как и ожидалось.

### Проверка честности через exec во все три контейнера

```bash
docker exec traefik-inside-docker-app1-1 python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/server-number').read())"
```

Три раза подряд к `app1` - стабильно `722`. То же самое для `app2` (`360`) и `app3` (`200`). Сопоставили с последовательностью - сходится идеально:

```
200(app3) → 722(app1) → 360(app2) → 722(app1) → 360(app2) → 200(app3) → 360(app2) → 200(app3) → 722(app1)
```

---

## Сценарий 3: Traefik внутри Kubernetes

У Traefik, в отличие от Caddy, есть давно существующий зрелый официальный Helm chart.

### Установка

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
```

Первая попытка установки зависла в `Pending`:

```
Warning FailedScheduling: 0/1 nodes are available: 1 node(s) didn't have free ports for the requested pod ports.
```

Проверил, что реально занимает порты на ноде:

```bash
minikube ssh "sudo ss -tlnp | grep 8443"
```

```
LISTEN *:8443 users:(("kube-apiserver",pid=2072,fd=4))
```

 `kube-apiserver` Minikube уже занимаел порт `8443` на ноде для себя, а я по умолчанию попыталися повесить туда же `hostPort` для Traefik. Переустановил с другим портом:

```bash
helm install traefik traefik/traefik \
  --namespace=traefik-system \
  --create-namespace \
  --set ports.web.hostPort=8095 \
  --set ports.websecure.hostPort=8444
```

После этого под встал в `Running`.

### Развёртывание приложения

```bash
eval $(minikube docker-env)
docker build -t traefik-demo-app:k8s .
```

`app-deployment.yml` (3 реплики) и `app-service.yml` (ClusterIP) - такие же, как в сценариях nginx/Caddy.

### IngressRoute - собственный ресурс Traefik

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-demo-route
spec:
  entryPoints:
    - web
  routes:
    - match: PathPrefix(`/`)
      kind: Rule
      services:
        - name: traefik-demo-service
          port: 80
```

Не стандартный K8s `Ingress`, а собственный CRD Traefik - Helm chart регистрирует его автоматически. Синтаксис заметно выразительнее - `match: PathPrefix(...)` вместо привычных `path`/`pathType`.

```bash
kubectl apply -f app-deployment.yml
kubectl apply -f app-service.yml
kubectl apply -f ingressroute.yml
```

### Тест

```bash
kubectl port-forward -n traefik-system service/traefik 8096:80 --address=0.0.0.0 &
for i in 1 2 3 4 5 6 7 8 9; do curl -s http://localhost:8096/api/server-number; echo; done
```

```
{"number":571}
{"number":741}
{"number":171}
{"number":741}
{"number":171}
{"number":571}
{"number":171}
{"number":571}
{"number":741}
```

Тот же самый EDF-паттерн, что и в двух предыдущих сценариях.

### Проверка честности через exec в поды

```bash
kubectl exec <под> -- python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/api/server-number').read())"
```

Три пода дали `171`, `571`, `741` соответственно - полностью сходится с последовательностью выше.

---

## Сравнение

Балансировщики решают одну и ту же задачу совершенно по-разному, и это видно на каждом шаге. nginx требует полностью ручной конфигурации - добавил реплику, правишь `nginx.conf`, делаешь `reload` - но зато его поведение самое предсказуемое: round-robin строго по кругу, без скрытых сюрпризов. Caddy решает ту же задачу заметно компактнее по синтаксису, но по факту остаётся таким же статичным, как nginx - разве что вносит свой сюрприз: дефолтный алгоритм у него не round-robin, а `random`. Traefik - единственный, кто реально умеет следить за инфраструктурой сам, но только если подключить настоящий provider (Docker labels, Kubernetes API), а не статичный файл, который использовал в двух первых сценариях - в таком режиме он ничем не лучше двух других, разве что его конфиг ещё и разбит на два файла вместо одного, что оказалось менее удобно на практике.

С балансировкой похожая история - у каждого своя степень предсказуемости. У nginx единственная неожиданность возникла в Kubernetes, где 12 параллельных воркеров создавали видимость "не по порядку", хотя это просто следствие числа ядер CPU конкретной ноды, а не свойство самого алгоритма. У Caddy сюрприз был сразу - `random` вместо ожидаемого round-robin. У Traefik сюрприз оказался ещё глубже: его дефолтный `wrr` работает через EDF-планирование и принципиально не даёт строгого цикла даже с одним процессом, в отличие от nginx, где непоследовательность - только побочный эффект многопоточности. То есть nginx предсказуем почти всегда, Caddy предсказуем только если явно указать `lb_policy`, а Traefik не будет строго предсказуем никогда, даже с самыми явными настройками - просто потому что так работает его алгоритм.

С HTTPS ситуация зеркальная. У nginx автоматического HTTPS нет вообще, нужен отдельный certbot. У Traefik он есть, но не включён по умолчанию - нужно осознанно подключать. У Caddy - единственного из трёх - автоматический HTTPS работает из коробки без единой настройки, это его главная фича. Но именно поэтому Caddy оказался единственным, кто создал проблему там, где HTTPS вообще не был нужен: официальный Ingress Controller форсировал редирект на HTTPS даже без настроенного email, и пришлось лезть в исходный код, чтобы это выключить. У nginx и Traefik такая ситуация просто не могла возникнуть, потому что ни один из них не навязывает HTTPS сам.

И это же напрямую отражается на зрелости интеграции с Kubernetes. nginx и Traefik - оба давно устоявшиеся решения, и единственные сложности, которые встретил, были чисто инфраструктурные, а не специфичные для самих инструментов: конфликт портов с воркерами у nginx объясняется числом ядер ноды, а конфликт `hostPort` с `kube-apiserver` у Traefik решился одной строчкой `--set`. Caddy же - единственный, чей официальный Ingress Controller прямо помечен как "work in progress", и это подтвердилось на практике: пока nginx и Traefik просто работали, с Caddy пришлось параллельно разбираться с HTTPS-редиректом, зависшим keep-alive-соединением через один Service-адрес и застрявшим webhook'ом от другого контроллера - заметно больше скрытых сложностей именно потому, что эта часть его экосистемы ещё не так обкатана, как у двух конкурентов.

### Разница видна и на живом примере конфига

Одна и та же задача - три бэкенда, балансировка round-robin - у каждого выглядит по-разному.

**nginx** - нужно объявить отдельный `upstream`-блок, потом сослаться на него в `server`:

```nginx
events {}

http {
    upstream backend {
        server app1:5000;
        server app2:5000;
        server app3:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

11 строк, три вложенных блока.

**Caddy** - то же самое, но заметно компактнее:

```
:80 {
    reverse_proxy app1:5000 app2:5000 app3:5000 {
        lb_policy round_robin
    }
}
```

5 строк, один блок. При этом важно помнить - без явного `lb_policy round_robin` тут по умолчанию был бы `random`.

**Traefik** - тут простота обманчива, потому что конфиг разбит на два файла. Static-часть (`traefik.yml`):

```yaml
entryPoints:
  web:
    address: ":80"

providers:
  file:
    filename: /etc/traefik/dynamic.yml
```

И dynamic-часть (`dynamic.yml`):

```yaml
http:
  services:
    backend:
      loadBalancer:
        servers:
          - url: "http://app1:5000"
          - url: "http://app2:5000"
          - url: "http://app3:5000"

  routers:
    my-router:
      rule: "PathPrefix(`/`)"
      service: backend
```

Два файла, суммарно строк побольше чем у Caddy - но это только пока используется файловый provider. Если подключить настоящий Docker/Kubernetes provider - весь блок `services` с ручным перечислением адресов вообще не понадобится, Traefik найдёт бэкенды сам.

---

## Итог - что для чего лучше подходит

**nginx** - если нужна максимальная предсказуемость и производительность на стабильной, редко меняющейся инфраструктуре. Топология бэкендов известна заранее и меняется нечасто. Хорошо подходит когда важна зрелость экосистемы (как Ingress Controller - самый проверенный вариант из всех трёх). Минус - любое изменение списка бэкендов требует ручной правки конфига и `reload`.

**Caddy** - если для проекта критичен автоматический HTTPS без единой ручной настройки сертификатов, и хочется максимально простой синтаксис конфига. Отлично подходит для небольших/средних проектов вне Kubernetes. В связке с Kubernetes стоит быть аккуратнее - официальный Ingress Controller всё ещё в статусе "WIP", и  на практике поймал несколько неочевидных особенностей (авто-HTTPS-редирект, sticky-поведение через один Service-адрес).

**Traefik** - если инфраструктура сама по себе динамическая: контейнеры регулярно создаются и удаляются, реплики масштабируются туда-сюда, используется настоящий Docker/Kubernetes provider (не статичный файл, как в outside-docker/inside-docker тестах). Это тот случай, когда балансировщик сам должен знать про изменения в инфраструктуре, а не сверяться с зафиксированным конфигом. Минус - придётся принять, что балансировка не будет выглядеть как красивый строгий цикл 1→2→3, хотя по факту она полностью честная.