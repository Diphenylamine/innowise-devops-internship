# Module 14 - Kubernetes Ingress + Helm

## NodePort vs LoadBalancer vs Ingress

**NodePort** - открывает порт на каждой ноде (например `192.168.49.2:30955`). Для каждого сервиса свой порт, пользователь должен знать конкретный номер. Неудобно и некрасиво.

**LoadBalancer** - даёт один внешний IP, но в облаке каждый LoadBalancer стоит денег (отдельный облачный IP на каждый сервис).

**Ingress** - одна точка входа с маршрутизацией по URL (L7). Один IP обслуживает много сервисов по разным путям и хостам:

```
my-app.local/       → my-app-service
my-app.local/api    → api-service
```

## Включение Ingress Controller

```bash
minikube addons enable ingress
```

```
🌟  The 'ingress' addon is enabled
```

Проверка что контроллер запущен:

```bash
kubectl get pods -n ingress-nginx
```

```
NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-controller-596f8778bc-j4cjx   1/1     Running     0          4m38s
```

## app-ingress.yml

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

```bash
kubectl apply -f app-ingress.yml
kubectl get ingress
```

```
NAME             CLASS   HOSTS          ADDRESS        PORTS   AGE
my-app-ingress   nginx   my-app.local   192.168.49.2   80      3m
```

## Проблема: Ingress недоступен снаружи WSL2 и её решение

Основной задачей было достучаться до приложения через Ingress снаружи кластера. Здесь столкнулся с проблемой сетевой изоляции.

### Симптом

```bash
curl http://192.168.49.2/
```

Соединение устанавливалось (`Connected to 192.168.49.2 port 80`), но ответа не было - запрос висел до таймаута.

### Шаг 1 - проверка что Ingress вообще работает

Проверили изнутри кластера, зайдя прямо в под Ingress Controller:

```bash
kubectl exec -it -n ingress-nginx deployment/ingress-nginx-controller -- \
  curl http://my-app-service.default.svc.cluster.local/
```

```
{"message":"Привет!."}
```

Вывод: **Ingress и приложение полностью исправны**. Проблема не в кластере, а в сети между WSL и Minikube.

### Шаг 2 - проверка сетевой доступности

```bash
ping -c 3 192.168.49.2
```

```
3 packets transmitted, 0 received, 100% packet loss
```

IP Minikube вообще недоступен из WSL. Причина: **Docker driver в WSL2 создаёт изолированную сеть**, которая не маршрутизируется в WSL2 (у WSL2 своя виртуальная сеть в отдельной VM).

### Шаг 3 - неудачные попытки

- `minikube tunnel` - требовал запущенный кластер, при Docker driver на WSL2 не пробрасывал сеть.
- `ip route add 192.168.49.0/24 via 192.168.49.1` - `Nexthop has invalid gateway` (шлюз недоступен из WSL).
- `socat TCP-LISTEN:8888 → 192.168.49.2:80` - socat принимал запрос, но не мог доставить его до Minikube (тот же `ping` показывал 100% loss).
- Смена драйвера на `none` - `iptables not found`.
- Смена драйвера на `podman` - `can't talk to a V1 container registry`.
- `netsh portproxy` из Windows - пробрасывал только до WSL2, но не до сети Minikube внутри него.

### Шаг 4 - решение через kubectl port-forward

Ключевая идея: `kubectl port-forward` не использует сетевую маршрутизацию Minikube. Он туннелирует трафик **через Kubernetes API server**, который kubectl уже умеет находить (раз все команды `kubectl get` работают).

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80 --address=0.0.0.0 &
curl -H "Host: my-app.local" http://localhost:8080/
```

```
{"message":"Привет!."}
```

Решение найдено, трафик пошёл в обход изолированной сети.

### Шаг 5 - доступ через браузер по красивому URL

Добавил в Windows `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 my-app.local
```

Браузер по `http://my-app.local:8080/` добавлял порт в заголовок Host (`my-app.local:8080`), что вызывало `Bad Request - Invalid Hostname`. Чтобы браузер не добавлял порт, нужен был проброс на порт 80.

Порт 80 оказался занят локальным nginx:
```bash
sudo ss -tlnp | grep :80
# LISTEN 0 511 0.0.0.0:80 users:(("nginx",pid=9238))
```

Остановил его и запустил port-forward на 80:

```bash
sudo systemctl stop nginx
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80 --address=0.0.0.0 &
```

После этого `http://my-app.local/` открылся в браузере Windows.

### Вывод

`kubectl port-forward` - это стандартный способ достучаться до сервисов в кластере с локальной машины, работающий независимо от драйвера и ОС. Именно так эта задача и решается на реальных проектах, где кластер обычно вообще в облаке с реальным внешним IP.

## Проверка host-based routing

```bash
curl -H "Host: my-app.local" http://localhost:8080/
```

```
{"message":"Привет!."}
```

Ingress различает сайты по заголовку `Host` - запрос с `Host: my-app.local` корректно маршрутизируется на `my-app-service`.

## Helm - пакетный менеджер Kubernetes

Helm - это "apt/pip для Kubernetes". В модуле 13 для развёртывания Postgres вручную написал 6 YAML-файлов (Secret, ConfigMap, PVC, Deployment, Service, my-app-configmap). Helm разворачивает весь такой набор одной командой.

- **Chart** - пакет Helm с шаблонами всех YAML (аналог `.deb`).
- **Release** - установленный экземпляр chart в кластере.

### Установка Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

```
version.BuildInfo{Version:"v3.21.2", GitCommit:"...", GoVersion:"go1.26.4"}
```

### Добавление репозитория

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

```
"bitnami" has been added to your repositories
Update Complete. ⎈Happy Helming!⎈
```

### Удаление ручного Postgres из модуля 13

```bash
kubectl delete deployment postgres-deployment
kubectl delete service postgres-db
kubectl delete pvc postgres-pvc
kubectl delete configmap postgres-configmap
kubectl delete secret postgres-secret
```

### Установка Postgres через Helm

```bash
helm install my-pg bitnami/postgresql
```

```
NAME: my-pg
STATUS: deployed
REVISION: 1
CHART NAME: postgresql
CHART VERSION: 18.7.10
```

Проверка:

```bash
helm list
```

```
NAME    NAMESPACE   REVISION   STATUS      CHART                APP VERSION
my-pg   default     1          deployed    postgresql-18.7.10   18.4.0
```

```bash
kubectl get pods
```

```
NAME                 READY   STATUS    RESTARTS   AGE
my-pg-postgresql-0   1/1     Running   0          68s
```

Имя пода `my-pg-postgresql-0` с индексом `0` - признак **StatefulSet**. Helm использовал StatefulSet вместо Deployment, потому что для баз данных нужны стабильные сетевые имена и привязка к хранилищу. Всё это (Secret с паролем, Service, PVC, StatefulSet) Helm создал автоматически одной командой - то, что в модуле 13 делал руками.