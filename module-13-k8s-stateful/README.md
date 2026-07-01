# Module 13 - Kubernetes Stateful: ConfigMap, Secret, PVC

## ConfigMap vs Secret

**ConfigMap** - хранит не-секретные конфиги в plain text. Любой в кластере может прочитать.
Используется для: `POSTGRES_DB`, `POSTGRES_USER`, `DATABASE_URL`.

**Secret** - хранит пароли, ключи в base64. K8s ограничивает доступ к ним через RBAC и не логирует их значения.
Используется для: `POSTGRES_PASSWORD`.

Base64 - это не шифрование, просто сигнал K8s что данные чувствительные.

## postgres-secret.yml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: "mysecret"
```

```bash
kubectl apply -f postgres-secret.yml
```

```
secret/postgres-secret created
```

## postgres-configmap.yml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-configmap
data:
  POSTGRES_DB: "devopsdb"
  POSTGRES_USER: "devops"
```

```bash
kubectl apply -f postgres-configmap.yml
```

```
configmap/postgres-configmap created
```

## PV и PVC

PV (PersistentVolume) - физический диск в кластере. Администратор создаёт заранее.

PVC (PersistentVolumeClaim) - запрос от приложения: "мне нужно 1 ГБ". K8s сам находит подходящий PV и связывает его с PVC.

Разделение ответственности: администратор управляет дисками (PV), разработчик просто запрашивает место (PVC).

В Minikube PV создаётся автоматически при создании PVC.

## postgres-pvc.yml

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f postgres-pvc.yml
kubectl get pvc
```

```
NAME           STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
postgres-pvc   Bound    pvc-4550b616-ae18-45e0-90ae-063ec7b4c9fb   1Gi        RWO            standard       13s
```

Статус `Bound` - Minikube автоматически создал PV и связал его с PVC.

## postgres-deployment.yml

Объединяет Secret, ConfigMap и PVC через `envFrom` и `volumeMounts`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:14-alpine
          envFrom:
            - configMapRef:
                name: postgres-configmap
            - secretRef:
                name: postgres-secret
          volumeMounts:
            - name: pg-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: pg-data
          persistentVolumeClaim:
            claimName: postgres-pvc
```

```bash
kubectl apply -f postgres-deployment.yml
kubectl get pods -l app=postgres
```

```
NAME                                  READY   STATUS    RESTARTS   AGE
postgres-deployment-c97b55d9d-pkc94   1/1     Running   0          35s
```

## postgres-service.yml

Service типа `ClusterIP` - доступен только внутри кластера.
DNS-имя `postgres-db` автоматически создаётся K8s и доступно всем подам кластера.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-db
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

```bash
kubectl apply -f postgres-service.yml
kubectl get services
```

```
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
kubernetes       ClusterIP   10.96.0.1       <none>        443/TCP        15h
my-app-service   NodePort    10.99.245.193   <none>        80:30955/TCP   19m
postgres-db      ClusterIP   10.102.151.94   <none>        5432/TCP       13s
```

## my-app-configmap.yml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-configmap
data:
  DATABASE_URL: "postgresql://devops:mysecret@postgres-db:5432/devopsdb"
```

`postgres-db` - это DNS-имя Service из предыдущего шага. K8s автоматически резолвит его в IP Postgres пода.

```bash
kubectl apply -f my-app-configmap.yml
```

## Обновление my-app Deployment

Добавляем `envFrom` в `app-deployment.yml` чтобы my-app получил `DATABASE_URL`:

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
          envFrom:
            - configMapRef:
                name: my-app-configmap
```

```bash
kubectl apply -f app-deployment.yml
kubectl get pods -l app=my-app
```

```
NAME                                READY   STATUS    RESTARTS   AGE
my-app-deployment-f7b767fc4-7gwfj   1/1     Running   0          6s
my-app-deployment-f7b767fc4-mwh5r   1/1     Running   0          3s
my-app-deployment-f7b767fc4-r2fm7   1/1     Running   0          4s
```

Все 3 пода перезапустились с новой конфигурацией. my-app подключается к Postgres через K8s DNS: `postgres-db:5432`.

## Проверка подключения my-app к Postgres

Заходим внутрь пода my-app и проверяем переменную окружения:

```bash
kubectl exec -it my-app-deployment-f7b767fc4-7gwfj -- bash
echo $DATABASE_URL
```

```
postgresql://devops:mysecret@postgres-db:5432/devopsdb
```

Проверяем реальное подключение к Postgres через K8s DNS:

```bash
psql postgresql://devops:mysecret@postgres-db:5432/devopsdb -c "\l"
```

```
                                                 List of databases
   Name    | Owner  | Encoding |  Collate   |   Ctype    |
-----------+--------+----------+------------+------------+
 devopsdb  | devops | UTF8     | en_US.utf8 | en_US.utf8 |
 postgres  | devops | UTF8     | en_US.utf8 | en_US.utf8 |
 template0 | devops | UTF8     | en_US.utf8 | en_US.utf8 |
 template1 | devops | UTF8     | en_US.utf8 | en_US.utf8 |
(4 rows)
```

my-app успешно подключился к Postgres через K8s DNS `postgres-db:5432`.
Вся цепочка работает: ConfigMap -> DATABASE_URL -> K8s DNS -> Service -> Postgres pod.