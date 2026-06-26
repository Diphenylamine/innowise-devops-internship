# Module 06 — Docker Compose Advanced

## .env и переменные окружения

Секреты не должны храниться в `docker-compose.yml` напрямую.
Вместо этого создаём файл `.env` в корне проекта:

```
POSTGRES_USER=devops
POSTGRES_PASSWORD=mysecret
```

В `docker-compose.yml` используем переменные через `${}`:

```yaml
environment:
 - POSTGRES_USER=${POSTGRES_USER}
 - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
 - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/devops_db
```

Compose автоматически подтягивает переменные из `.env` файла.
Файл `.env` добавляется в `.gitignore` - секреты не попадают в репозиторий.

## docker-compose.yml

```yaml
services:
  app:
    build: ./app
    ports:
      - "5000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/devops_db
    volumes:
      - ./app:/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devops"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:alpine

volumes:
  postgres-data:
```

## Запуск

```bash
docker-compose up

[+] up 1/1
 ✔ Container module-06-docker-compose-advanced-app-1 Recreated                                                                                                                                                                           0.2s
Attaching to app-1, db-1, redis-1
Container module-06-docker-compose-advanced-db-1 Waiting
redis-1  | Starting Redis Server
redis-1  | 1:C 26 Jun 2026 03:39:05.709 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1  | 1:C 26 Jun 2026 03:39:05.709 * Redis version=8.8.0, bits=64, commit=00000000, modified=1, pid=1, just started
redis-1  | 1:C 26 Jun 2026 03:39:05.709 * Configuration loaded
redis-1  | 1:M 26 Jun 2026 03:39:05.710 * monotonic clock: POSIX clock_gettime
redis-1  | 1:M 26 Jun 2026 03:39:05.712 * Running mode=standalone, port=6379.

redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf> RedisBloom version 8.8.0 (Git=unknown)
db-1     | 
db-1     | PostgreSQL Database directory appears to contain a database; Skipping initialization

redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf> Registering configuration options: [
db-1     | 
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { bf-error-rate       :      0.01 }
db-1     | 2026-06-26 03:39:05.847 UTC [1] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { bf-initial-size     :       100 }

db-1     | 2026-06-26 03:39:05.847 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { bf-expansion-factor :         2 }

db-1     | 2026-06-26 03:39:05.847 UTC [1] LOG:  listening on IPv6 address "::", port 5432
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { cf-bucket-size      :         2 }
db-1     | 2026-06-26 03:39:05.851 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { cf-initial-size     :      1024 }
db-1     | 2026-06-26 03:39:05.858 UTC [27] LOG:  database system was shut down at 2026-06-26 03:39:02 UTC

redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { cf-max-iterations   :        20 }

db-1     | 2026-06-26 03:39:05.867 UTC [1] LOG:  database system is ready to accept connections

redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf> a{ cf-expansion-factor :         1 }
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf>  { cf-max-expansions   :        32 }
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * <bf> ]
redis-1  | 1:M 26 Jun 2026 03:39:05.713 * Module 'bf' loaded from /usr/local/lib/redis/modules//redisbloom.so
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> search-workers default: 12 (min of MAX_WORKER_THREADS=16 and CPU cores)
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> Redis version found by RedisSearch : 8.8.0 - oss
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> RediSearch version 8.8.0 (Git=d2ae026)
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> Low level api version 1 initialized successfully
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> gc: ON, prefix min length: 2, min word length to stem: 4, prefix max expansions: 200, query timeout (ms): 500, timeout policy: return, oom policy: return, cursor read size: 1000, cursor
max idle (ms): 300000, max doctable size: 1000000, max number of search results:  1000000, default scorer: BM25STD,
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> Initialized thread pools!
redis-1  | 1:M 26 Jun 2026 03:39:05.724 * <search> Enabled workers threadpool of size 12
redis-1  | 1:M 26 Jun 2026 03:39:05.742 * <search> Subscribe to config changes
redis-1  | 1:M 26 Jun 2026 03:39:05.742 * <search> Subscribe to cluster slot migration events
redis-1  | 1:M 26 Jun 2026 03:39:05.742 * <search> Enabled role change notification
redis-1  | 1:M 26 Jun 2026 03:39:05.743 * <search> Cluster configuration: AUTO partitions, type: 0, coordinator timeout: 0ms
redis-1  | 1:M 26 Jun 2026 03:39:05.743 * Module 'search' loaded from /usr/local/lib/redis/modules//redisearch.so
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> RedisTimeSeries version 80800, git_sha=42ca4f1078fca732b7f9256adbf25914d67e1cc9
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> Redis version found by RedisTimeSeries : 8.8.0 - oss
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> Registering configuration options: [
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-compaction-policy   :              }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-num-threads         :            3 }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-libmr-protocol      :     INTERNAL }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-retention-policy    :            0 }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-duplicate-policy    :        block }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-chunk-size-bytes    :         4096 }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-encoding            :   compressed }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-ignore-max-time-diff:            0 }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries>  { ts-ignore-max-val-diff :     0.000000 }
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> ]
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> Detected redis oss
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> Subscribe to ASM events
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * <timeseries> Enabled diskless replication
redis-1  | 1:M 26 Jun 2026 03:39:05.745 * Module 'timeseries' loaded from /usr/local/lib/redis/modules//redistimeseries.so
redis-1  | 1:M 26 Jun 2026 03:39:05.749 * <ReJSON> Created new data type 'ReJSON-RL'
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> version: 80800 git sha: unknown branch: unknown
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V1 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V2 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V3 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V4 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V5 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V6 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Exported RedisJSON_V7 API
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Enabled diskless replication
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <ReJSON> Initialized shared string cache, thread safe: true.
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * Module 'ReJSON' loaded from /usr/local/lib/redis/modules//rejson.so
redis-1  | 1:M 26 Jun 2026 03:39:05.750 * <search> Acquired RedisJSON_V7 API
redis-1  | 1:M 26 Jun 2026 03:39:05.751 * Server initialized
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * <search> Loading event started
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * Loading RDB produced by version 8.8.0
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * RDB age 3 seconds
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * RDB memory usage when created 1.27 Mb
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * Done loading RDB, keys loaded: 0, keys expired: 0.
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * <search> Loading event ended successfully
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * DB loaded from disk: 0.001 seconds
redis-1  | 1:M 26 Jun 2026 03:39:05.752 * Ready to accept connections tcp
redis-1  | 1:M 26 Jun 2026 03:39:05.752 # WARNING: Redis does not require authentication and is not protected by network restrictions. Redis will accept connections from any IP address on any network interface.
Container module-06-docker-compose-advanced-db-1 Healthy
app-1    | INFO:     Started server process [1]
app-1    | INFO:     Waiting for application startup.
app-1    | INFO:     Application startup complete.
app-1    | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

## Healthcheck и depends_on

По умолчанию `depends_on` ждёт пока контейнер запустится.
Но база данных может быть не готова принимать подключения даже после старта.

`healthcheck` проверяет готовность сервиса командой `pg_isready`:

```yaml
db:
 healthcheck:
   test: ["CMD-SHELL", "pg_isready -U devops"]
   interval: 5s
   timeout: 5s
   retries: 5
```

`depends_on` с `condition: service_healthy` заставляет `app` ждать
пока `db` не пройдёт healthcheck:

```yaml
app:
 depends_on:
   db:
     condition: service_healthy
```

Результат в логах:
```
Container module-06-docker-compose-advanced-db-1 Healthy
app-1    | INFO: Uvicorn running on http://0.0.0.0:5000
```

`app` запустился только после того как `db` стал `Healthy`.

## Масштабирование

Запуск 3 инстансов `app` одной командой:

```bash
docker-compose up -d --scale app=3
```

```bash
docker-compose ps

NAME                                    IMAGE                                   PORTS
module-06-docker-compose-advanced-app-1  module-06-docker-compose-advanced-app  0.0.0.0:58072->5000/tcp
module-06-docker-compose-advanced-app-2  module-06-docker-compose-advanced-app  0.0.0.0:58069->5000/tcp
module-06-docker-compose-advanced-app-3  module-06-docker-compose-advanced-app  0.0.0.0:58071->5000/tcp
```

Docker автоматически назначил разные порты на хосте - поэтому
в `docker-compose.yml` используется `"5000"` без фиксации порта хоста,
иначе 3 контейнера не смогут слушать один и тот же порт.

Все три инстанса возвращают одинаковый ответ:
```json
{"message": "Привет!"}
```

В реальном проекте перед ними стоит load balancer (например Nginx),
который распределяет запросы между инстансами.
