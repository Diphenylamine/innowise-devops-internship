# Module 10 — Kubernetes Basics

## Что такое Kubernetes (кратко)

Kubernetes (K8s) — оркестратор контейнеров. Решает проблемы которые не решает Docker Compose: self-healing (автоматический перезапуск упавших подов на любой ноде кластера), горизонтальное масштабирование на несколько серверов, и zero-downtime деплой через Rolling Update.

Подробное сравнение с Docker Compose — в `essay-k8s.md`.

## Установка kubectl

`kubectl` — CLI для управления Kubernetes-кластером.

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

```
Client Version: v1.36.2
Kustomize Version: v5.8.1
```

## Установка minikube

`minikube` — локальный однонодовый Kubernetes-кластер для разработки и обучения.

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```

```
minikube version: v1.38.1
commit: c93a4cb9311efc66b90d33ea03f75f2c4120e9b0
```

## Запуск кластера

```bash
minikube start --driver=docker
```

```
Starting "minikube" primary control-plane node in "minikube" cluster
Creating docker container (CPUs=2, Memory=3400MB) ...
Preparing Kubernetes v1.35.1 on Docker 29.2.1 ...
Configuring bridge CNI (Container Networking Interface) ...
Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Minikube запускает кластер K8s внутри Docker-контейнера на хосте.

## Проверка кластера

```bash
kubectl get nodes
```

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   66m   v1.35.1
```

Одна нода `minikube` в роли `control-plane` — она же "мозг" кластера и единственный worker для подов.

## K8s объекты — теория

Четыре ключевых объекта:

Pod — минимальная единица K8s, обёртка над одним или несколькими контейнерами. Эфемерен: если падает — никто не пересоздаёт его сам, пока нет Deployment.

Deployment — контроллер, который декларирует желаемое количество подов ("хочу 3 реплики") и постоянно следит за фактическим состоянием, пересоздавая упавшие поды на любой живой ноде. Источник self-healing.

Service — даёт стабильный IP и DNS-имя для группы подов, балансирует трафик между ними. Решает проблему scaling из модуля 6 — не нужно вручную следить на каких портах какие реплики живут.

ConfigMap / Secret — хранилище конфигурации и чувствительных данных отдельно от образа приложения.

## Императивный запуск Pod

Запуск Pod напрямую, без YAML-манифеста:

```bash
kubectl run my-nginx --image=nginx
```

```
pod/my-nginx created
```

## Управление Pod'ом

```bash
kubectl get pods
```

```
NAME       READY   STATUS    RESTARTS   AGE
my-nginx   1/1     Running   0          3m26s
```

```bash
kubectl describe pod my-nginx
```

```
Name:             my-nginx
Node:             minikube/192.168.49.2
Status:           Running
IP:               10.244.0.3
Containers:
  my-nginx:
    Image:          nginx
    State:          Running
    Ready:          True

Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Scheduled  3m46s  default-scheduler  Successfully assigned default/my-nginx to minikube
  Normal  Pulling    3m47s  kubelet            Pulling image "nginx"
  Normal  Pulled     3m36s  kubelet            Successfully pulled image "nginx" in 11.238s
  Normal  Created    3m35s  kubelet            Container created
  Normal  Started    3m35s  kubelet            Container started
```

`IP: 10.244.0.3` — внутренний IP пода в сети кластера, недоступен напрямую снаружи (для внешнего доступа нужен Service).

`Events` — полная история жизненного цикла пода глазами kubelet, полезна для диагностики проблем со стартом контейнера.

## Очистка

```bash
kubectl delete pod my-nginx
```

```
pod "my-nginx" deleted from default namespace
```