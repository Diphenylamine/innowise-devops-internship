# Module 12 - Kubernetes Deployment

## Декларативность

Декларативный подход - описываешь желаемое состояние ("хочу 3 реплики"), а K8s сам разбирается как это обеспечить и поддерживает это состояние постоянно.

Императивный подход - описываешь каждый шаг ("запусти контейнер, потом ещё один, потом ещё один"). Если что-то упало - сам разбирайся.

Разница в том кто отвечает за результат: при декларативном подходе это K8s, при императивном - человек.

## Сборка образа для Minikube

Minikube использует свой внутренний Docker daemon. Чтобы собранный образ был виден K8s - нужно переключиться на него:

```bash
eval $(minikube docker-env)
docker build -t my-app:k8s .
```

```bash
docker images | grep my-app
```

```
my-app:k8s   7af50920245e   162MB
```

`imagePullPolicy: IfNotPresent` в Deployment обязателен - без него K8s попытается скачать образ из Docker Hub и получит ошибку `ErrImagePull`.

## app-deployment.yml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:k8s
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
```

```bash
kubectl apply -f app-deployment.yml
```

```
deployment.apps/my-app-deployment created
```

```bash
kubectl get pods -l app=my-app
```

```
NAME                                 READY   STATUS    RESTARTS   AGE
my-app-deployment-77679cb4c4-2gj2l   1/1     Running   0          4s
my-app-deployment-77679cb4c4-8wcc2   1/1     Running   0          2s
my-app-deployment-77679cb4c4-l4djq   1/1     Running   0          3s
```

## Self-healing

Удаляем один под:

```bash
kubectl delete pod my-app-deployment-77679cb4c4-2gj2l
```

Сразу проверяем:

```bash
kubectl get pods -l app=my-app
```

```
NAME                                 READY   STATUS    RESTARTS   AGE
my-app-deployment-77679cb4c4-8wcc2   1/1     Running   0          32s
my-app-deployment-77679cb4c4-l4djq   1/1     Running   0          33s
my-app-deployment-77679cb4c4-l8frd   1/1     Running   0          5s
```

Под `2gj2l` удалён - Deployment немедленно создал новый `l8frd` (AGE: 5s).
Deployment постоянно следит за количеством реплик и восстанавливает их до нужного числа без участия человека.

## app-service.yml

Service даёт стабильный IP и DNS-имя для группы подов, балансирует трафик между ними.
`selector: app: my-app` - Service находит все поды с этим label.
`type: NodePort` - выставляет сервис наружу кластера.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 5000
  type: NodePort
```

```bash
kubectl apply -f app-service.yml
kubectl get services
```

```
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
kubernetes       ClusterIP   10.96.0.1       <none>        443/TCP        14h
my-app-service   NodePort    10.99.245.193   <none>        80:30955/TCP   26s
```

## Тестирование

```bash
minikube service my-app-service
```

```
┌───────────┬────────────────┬─────────────┬────────────────────────┐
│ NAMESPACE │      NAME      │ TARGET PORT │          URL           │
├───────────┼────────────────┼─────────────┼────────────────────────┤
│ default   │ my-app-service │             │ http://127.0.0.1:36333 │
└───────────┴────────────────┴─────────────┴────────────────────────┘
```

Приложение доступно по `http://127.0.0.1:36333` - FastAPI возвращает JSON ответ.