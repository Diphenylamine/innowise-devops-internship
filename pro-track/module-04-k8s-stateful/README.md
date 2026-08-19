# Pro Track - Модуль 4: K8s 101 (StatefulSet и Хранилища)

**Цель модуля:** перейти от Deployment (для stateless) к StatefulSet (для stateful приложений типа БД).

---

## Задача 1: Теория - Deployment vs. StatefulSet

Deployment проектировался для stateless-приложений - там, где под не хранит данные, которые должны пережить его собственный рестарт, и где любой под функционально взаимозаменяем с любым другим. Отсюда две ключевые характеристики Deployment: имена подов случайные (`app-1a2b3c`, `app-4d5e6f`), и при рестарте под получает новый PersistentVolume - Deployment не гарантирует переподключение к тому же диску.

Для базы данных обе особенности фатальны:

1. **Нужны стабильные сетевые имена** - реплика в кластерной БД должна находить мастера по предсказуемому адресу. StatefulSet даёт стабильное имя (`pg-0`, `pg-1`, `pg-2`) и персональное DNS-имя через headless service (`pg-0.postgres-headless`).
2. **Нужны стабильные диски** - при рестарте Deployment под может оказаться на другом PV, что для БД означает потерю данных. `volumeClaimTemplates` StatefulSet присваивает каждой реплике персональный PVC (`data-pg-0`, `data-pg-1`...), который переподключается при пересоздании пода с тем же именем.
3. **Порядок запуска** - StatefulSet запускает/останавливает поды **последовательно** (по возрастанию индекса), а не параллельно - критично, когда master должен подняться раньше реплик.

---

## Задача 2: Теория - StorageClass (SC)

**Описание:** StorageClass - "драйвер" для динамического создания дисков. Критерий - `kubectl get sc` показывает `standard (default)`.

**Решение:**

```bash
kubectl get sc
```

NAME PROVISIONER RECLAIMPOLICY VOLUMEBINDINGMODE ALLOWVOLUMEEXPANSION AGE
standard (default) k8s.io/minikube-hostpath Delete Immediate false 27d

---

## Задача 3: Теория - PersistentVolume (PV) и PersistentVolumeClaim (PVC)

**Описание:** PV - "кусок" диска, PVC - "запрос" на хранилище.

PV существует независимо от пода, представляет реально выделенное хранилище. PVC - запрос со стороны приложения ("хочу 5 ГБ"), который Kubernetes связывает с существующим или динамически создаваемым (через StorageClass) PV. Связка: PVC - интерфейс, PV - реализация, StorageClass - фабрика, которая эту реализацию создаёт по запросу.
```bash
kubectl get pv
kubectl get pvc
```

No resources found
No resources found in default namespace.

---

## Задача 4: `postgres-statefulset.yml`

**Описание:** создать манифест StatefulSet с `serviceName: "postgres-headless"`.

**Решение:**

Пароль вынесен в отдельный Secret 

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: "SuperSecretPass123"
  POSTGRES_USER: "postgres"
  POSTGRES_DB: "appdb"
```

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: pg
spec:
  serviceName: "postgres-headless"
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
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef: { name: postgres-secret, key: POSTGRES_USER }
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef: { name: postgres-secret, key: POSTGRES_PASSWORD }
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef: { name: postgres-secret, key: POSTGRES_DB }
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        storageClassName: "standard"
        resources:
          requests:
            storage: 1Gi
```

```bash
kubectl apply -f postgres-statefulset.yml --dry-run=client
```

statefulset.apps/pg created (dry run)

---

## Задача 5: `postgres-headless-service.yml`

**Описание:** headless service (`clusterIP: None`) для персональных DNS-имён подов.

**Решение:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
    - port: 5432
      name: postgres
```

```bash
kubectl apply -f postgres-headless-service.yml --dry-run=client
```

service/postgres-headless created (dry run)

---

## Задача 6: `volumeClaimTemplates`

**Описание:** в спеке StatefulSet описать `volumeClaimTemplates`. Критерий - `volumeClaimTemplates` описан.

**Решение:**

`volumeClaimTemplates` - не отдельный файл, а часть манифеста `postgres-statefulset.yml` (см. задачу 4), на одном уровне со `spec.template`:

```yaml
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        storageClassName: "standard"
        resources:
          requests:
            storage: 1Gi
```

Тест, что синтаксис валиден и `volumeClaimTemplates` реально принят кластером:
```bash
kubectl apply -f postgres-statefulset.yml --dry-run=client
```

statefulset.apps/pg created (dry run)

```bash
kubectl get pvc
```

NAME STATUS VOLUME CAPACITY ACCESS MODES STORAGECLASS AGE
data-pg-0 Bound pvc-ec871824-81dc-4cec-838f-350f5afac939 1Gi RWO standard 36s


Имя `data-pg-0` - это ровно `<имя из volumeClaimTemplates>-<имя пода>`, что и доказывает, что шаблон применяется автоматически для каждой реплики, а не создаётся вручную.

---

## Задача 7: Применение

**Описание:** `kubectl apply`. Критерий - `get statefulset` (1 Ready), `get pods` (`pg-0` Running), `get pvc` (`data-pg-0` Bound).

**Решение:**

```bash
kubectl apply -f postgres-secret.yml
kubectl apply -f postgres-headless-service.yml
kubectl apply -f postgres-statefulset.yml
```

```bash
kubectl get statefulset
kubectl get pods
kubectl get pvc
```

NAME READY AGE
pg 1/1 2m48s

NAME READY STATUS RESTARTS AGE
pg-0 1/1 Running 0 2m49s

NAME STATUS VOLUME CAPACITY ACCESS MODES STORAGECLASS AGE
data-pg-0 Bound pvc-ec871824-81dc-4cec-838f-350f5afac939 1Gi RWO standard 36s

---

## Задача 8: Масштабирование

**Описание:** `kubectl scale statefulset postgres --replicas=3`. Критерий - K8s последовательно запускает `pg-1` и `pg-2`.

**Решение:**

```bash
kubectl scale statefulset pg --replicas=3
```

Доказательство последовательности через события кластера :
```bash
kubectl get events --sort-by='.lastTimestamp' | grep -E "pg-1|pg-2"
```

2m31s Normal SuccessfulCreate statefulset/pg Create Claim data-pg-1 Pod pg-1 in StatefulSet pg success
2m31s Normal Scheduled pod/pg-1 Successfully assigned default/pg-1 to minikube
2m30s Normal Started pod/pg-1 Container started
2m29s Normal Scheduled pod/pg-2 Successfully assigned default/pg-2 to minikube
2m29s Normal SuccessfulCreate statefulset/pg Create Pod pg-2 in StatefulSet pg successful


`pg-2` начал создаваться только после того, как `pg-1` уже был `Started` - задержка всего 2 секунды объясняется тем, что образ `postgres:16-alpine` был уже локально закеширован (оба лога подтверждают `"already present on machine"`), поэтому старт очень быстрый, но порядок (`OrderedReady`) строго соблюдён, не параллельный.

```bash
kubectl get pvc
```

data-pg-0 Bound 1Gi ... 15m
data-pg-1 Bound 1Gi ... 2m38s
data-pg-2 Bound 1Gi ... 2m36s

---

## Задача 9: Failover

**Описание:** `kubectl delete pod pg-1`. Критерий - под перезапускается, подхватывает старый диск `data-pg-1`, данные не теряются.

**Решение:**

Записал тестовые данные до удаления:
```bash
kubectl exec -it pg-1 -- psql -U postgres -d appdb -c "CREATE TABLE failover_test (id serial PRIMARY KEY, note text); INSERT INTO failover_test (note) VALUES ('data survived before pod delete');"
kubectl exec -it pg-1 -- psql -U postgres -d appdb -c "SELECT * FROM failover_test;"
```

id | note
----+---------------------------------
1 | data survived before pod delete
(1 row)


Убил под:
```bash
kubectl delete pod pg-1
```

Под пересоздан (новый `AGE`), но тест показывает ту же строку:
```bash
kubectl exec -it pg-1 -- psql -U postgres -d appdb -c "SELECT * FROM failover_test;"
```

id | note
----+---------------------------------
1 | data survived before pod delete
(1 row)


PVC остался тем же объектом (не пересоздался, `AGE` отсчитывается с задачи 8, не с момента удаления пода):
```bash
kubectl get pvc data-pg-1
```

data-pg-1 Bound pvc-209f67c2-f77b-433d-a007-7e4e509cef00 1Gi RWO standard 6m39s


---

## Задача 10: MySQL и MongoDB через Helm

**Описание:** `helm install mysql bitnami/mysql` и `helm install mongo bitnami/mongodb`. Критерий - в кластере одновременно развёрнуты 3 разные СУБД (Postgres, MySQL, MongoDB).

**Решение:**

```bash
helm install mysql bitnami/mysql \
  --set image.repository=bitnamilegacy/mysql \
  --set global.security.allowInsecureImages=true

helm install mongo bitnami/mongodb \
  --set architecture=replicaset \
  --set image.repository=bitnamilegacy/mongodb \
  --set global.security.allowInsecureImages=true
```

Тест:
```bash
kubectl get pods
```

NAME READY STATUS RESTARTS AGE
mongo-mongodb-0 1/1 Running 0 3m1s
mongo-mongodb-1 1/1 Running 0 2m10s
mongo-mongodb-arbiter-0 1/1 Running 0 3m1s
mysql-0 1/1 Running 0 5m3s
pg-0 1/1 Running 0 7m35s
pg-1 1/1 Running 0 7m13s
pg-2 1/1 Running 0 7m12s


```bash
kubectl exec -it mongo-mongodb-0 -- mongosh admin --eval "rs.status()" -u root -p "$MONGO_PASS"
```

members: [
{ name: 'mongo-mongodb-0...', stateStr: 'PRIMARY', health: 1 },
{ name: 'mongo-mongodb-arbiter-0...', stateStr: 'ARBITER', health: 1 },
{ name: 'mongo-mongodb-1...', stateStr: 'SECONDARY', health: 1, syncSourceHost: 'mongo-mongodb-0...' }
]


Все 3 СУБД реализованы через StatefulSet:
```bash
kubectl get statefulset
```

NAME READY AGE
mongo-mongodb 2/2 3m
mongo-mongodb-arbiter 1/1 3m
mysql 1/1 5m
pg 3/3 7m
