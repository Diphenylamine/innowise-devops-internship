# Module 05 — Docker Compose

Docker Compose — инструмент для запуска многоконтейнерных приложений.
`docker-compose.yml` — YAML описывающий сервисы,
сети и volumes. Вместо длинных `docker run` команд — один файл и одна команда.

## docker-compose.yml

```yaml
services:
  app:
    build: ./app
    ports:
      - "5000:5000"

  db:
    image: postgres:14-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: mysecret
```

## Запуск

```bash
docker-compose up

time="2026-06-26T05:57:57+03:00" level=warning msg="D:\\internship\\innowise-devops-internship\\module-05-docker-compose\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential co
nfusion"
[+] up 14/14
 ✔ Image postgres:14-alpine Pulled                                                                                                                                                                                                      16.8s
#1 [internal] load local bake definitions
#1 reading from stdin 621B done
#1 DONE 0.0s

#2 [internal] load build definition from Dockerfile
#2 transferring dockerfile: 211B done
#2 DONE 0.0s

#3 [internal] load metadata for docker.io/library/python:3.10-slim
#3 DONE 2.5s

#4 [internal] load .dockerignore
#4 transferring context: 2B done
#4 DONE 0.0s

#5 [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a
#5 resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a 0.0s done
#5 DONE 0.0s

#6 [internal] load build context
#6 transferring context: 430B done
#6 DONE 0.0s

#7 [3/4] COPY . .
#7 CACHED

#8 [2/4] WORKDIR /app
#8 CACHED

#9 [4/4] RUN pip install -r requirements.txt
#9 CACHED

#10 exporting to image
#10 exporting layers done
#10 exporting manifest sha256:585f4b066c6228aa13d68b192d5f6462bba39bef7df85ecf22de9eba42a8d52a 0.0s done
#10 exporting config sha256:5ec8001e565b949c49da6454c49d252a6b61bb71631c797d3af6ef8dcd6ea85a 0.0s done
#10 exporting attestation manifest sha256:b1c05ebd176c83cdfd9b9ae029ac3bc5cfb497da61e09453c7ce4fdf66babf58 0.0s done
#10 exporting manifest list sha256:3efa37887f7b9bc030ac3b88b3bfa45f898b4c67cdf76333061fb2883c742810 0.0s done
#10 naming to docker.io/library/module-05-docker-compose-app:latest done
#10 unpacking to docker.io/library/module-05-docker-compose-app:latest 0.0s done
#10 DONE 0.1s

[+] up 18/18g provenance for metadata file
 ✔ Image postgres:14-alpine                 Pulled                                                                                                                                                                                      16.8s
 ✔ Image module-05-docker-compose-app       Built                                                                                                                                                                                       3.2s
 ✔ Network module-05-docker-compose_default Created                                                                                                                                                                                     0.1s
 ✔ Container module-05-docker-compose-app-1 Created                                                                                                                                                                                     0.3s
 ✔ Container module-05-docker-compose-db-1  Created                                                                                                                                                                                     0.3s
Attaching to app-1, db-1
db-1  | The files belonging to this database system will be owned by user "postgres".
db-1  | This user must also own the server process.
db-1  | 
db-1  | The database cluster will be initialized with locale "en_US.utf8".
db-1  | The default database encoding has accordingly been set to "UTF8".
db-1  | The default text search configuration will be set to "english".
db-1  | 
db-1  | Data page checksums are disabled.
db-1  | 
db-1  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
db-1  | creating subdirectories ... ok
db-1  | selecting dynamic shared memory implementation ... posix
db-1  | selecting default max_connections ... 100
db-1  | selecting default shared_buffers ... 128MB
db-1  | selecting default time zone ... UTC
db-1  | creating configuration files ... ok
db-1  | running bootstrap script ... ok
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
db-1   | sh: locale: not found
db-1   | 2026-06-26 02:58:19.804 UTC [35] WARNING:  no usable system locales were found
db-1   | performing post-bootstrap initialization ... ok
db-1   | syncing data to disk ... ok
db-1   | 
db-1   | 
db-1   | Success. You can now start the database server using:
db-1   | 
db-1   |     pg_ctl -D /var/lib/postgresql/data -l logfile start
db-1   | 
db-1   | initdb: warning: enabling "trust" authentication for local connections
db-1   | You can change this by editing pg_hba.conf or using the option -A, or
db-1   | --auth-local and --auth-host, the next time you run initdb.
db-1   | waiting for server to start....2026-06-26 02:58:20.904 UTC [41] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 02:58:20.907 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 02:58:20.917 UTC [42] LOG:  database system was shut down at 2026-06-26 02:58:20 UTC
db-1   | 2026-06-26 02:58:20.928 UTC [41] LOG:  database system is ready to accept connections
db-1   |  done
db-1   | server started
db-1   | 
db-1   | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
db-1   | 
db-1   | waiting for server to shut down....2026-06-26 02:58:21.002 UTC [41] LOG:  received fast shutdown request
db-1   | 2026-06-26 02:58:21.005 UTC [41] LOG:  aborting any active transactions
db-1   | 2026-06-26 02:58:21.008 UTC [41] LOG:  background worker "logical replication launcher" (PID 48) exited with exit code 1
db-1   | 2026-06-26 02:58:21.008 UTC [43] LOG:  shutting down
db-1   | 2026-06-26 02:58:21.033 UTC [41] LOG:  database system is shut down
db-1   |  done
db-1   | server stopped
db-1   | 
db-1   | PostgreSQL init process complete; ready for start up.
db-1   | 
db-1   | 2026-06-26 02:58:21.136 UTC [1] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 02:58:21.137 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-06-26 02:58:21.137 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1   | 2026-06-26 02:58:21.141 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 02:58:21.146 UTC [54] LOG:  database system was shut down at 2026-06-26 02:58:21 UTC
db-1   | 2026-06-26 02:58:21.154 UTC [1] LOG:  database system is ready to accept connections
Gracefully Stopping... press Ctrl+C again to force
Container module-05-docker-compose-app-1 Killing
Container module-05-docker-compose-db-1 Killing ble Watch   d Detach
Container module-05-docker-compose-app-1 Stopping
Container module-05-docker-compose-db-1 Stopping
Container module-05-docker-compose-db-1 Killed
Container module-05-docker-compose-db-1 Stopped
Container module-05-docker-compose-app-1 Killed
Container module-05-docker-compose-app-1 Stopped
```

## Фоновый режим

```bash
docker-compose up -d

[+] up 2/2
 ✔ Container module-05-docker-compose-db-1  Started
 ✔ Container module-05-docker-compose-app-1 Started
```

## Управление


```bash
docker-compose ps
NAME                             IMAGE                          COMMAND                  SERVICE   CREATED         STATUS          PORTS
module-05-docker-compose-app-1   module-05-docker-compose-app   "uvicorn app:app --h…"   app       3 minutes ago   Up 23 seconds   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
module-05-docker-compose-db-1    postgres:14-alpine             "docker-entrypoint.s…"   db        3 minutes ago   Up 23 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```

## Просмотр логов

```bash
docker-compose logs app
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
app-1  | INFO:     Shutting down
app-1  | INFO:     Waiting for application shutdown.
app-1  | INFO:     Application shutdown complete.
app-1  | INFO:     Finished server process [1]
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

```bash
docker-compose logs -f
>> 
db-1  | The files belonging to this database system will be owned by user "postgres".
db-1  | This user must also own the server process.
db-1  | 
db-1  | The database cluster will be initialized with locale "en_US.utf8".
db-1  | The default database encoding has accordingly been set to "UTF8".
db-1  | The default text search configuration will be set to "english".
db-1  | 
db-1  | Data page checksums are disabled.
db-1  | 
db-1  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
db-1  | creating subdirectories ... ok
db-1  | selecting dynamic shared memory implementation ... posix
db-1   | selecting default max_connections ... 100
db-1   | selecting default shared_buffers ... 128MB
db-1   | selecting default time zone ... UTC
db-1   | creating configuration files ... ok
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
db-1   | running bootstrap script ... ok
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
app-1  | INFO:     Shutting down
app-1  | INFO:     Waiting for application shutdown.
app-1  | INFO:     Application shutdown complete.
app-1  | INFO:     Finished server process [1]
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
db-1   | sh: locale: not found
db-1   | 2026-06-26 02:58:19.804 UTC [35] WARNING:  no usable system locales were found
db-1   | performing post-bootstrap initialization ... ok
db-1   | syncing data to disk ... ok
db-1   | 
db-1   | 
db-1   | Success. You can now start the database server using:
db-1   | 
db-1   |     pg_ctl -D /var/lib/postgresql/data -l logfile start
db-1   | 
db-1   | initdb: warning: enabling "trust" authentication for local connections
db-1   | You can change this by editing pg_hba.conf or using the option -A, or
db-1   | --auth-local and --auth-host, the next time you run initdb.
db-1   | waiting for server to start....2026-06-26 02:58:20.904 UTC [41] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 02:58:20.907 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 02:58:20.917 UTC [42] LOG:  database system was shut down at 2026-06-26 02:58:20 UTC
db-1   | 2026-06-26 02:58:20.928 UTC [41] LOG:  database system is ready to accept connections
db-1   |  done
db-1   | server started
db-1   | 
db-1   | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
db-1   | 
db-1   | waiting for server to shut down....2026-06-26 02:58:21.002 UTC [41] LOG:  received fast shutdown request
db-1   | 2026-06-26 02:58:21.005 UTC [41] LOG:  aborting any active transactions
db-1   | 2026-06-26 02:58:21.008 UTC [41] LOG:  background worker "logical replication launcher" (PID 48) exited with exit code 1
db-1   | 2026-06-26 02:58:21.008 UTC [43] LOG:  shutting down
db-1   | 2026-06-26 02:58:21.033 UTC [41] LOG:  database system is shut down
db-1   |  done
db-1   | server stopped
db-1   | 
db-1   | PostgreSQL init process complete; ready for start up.
db-1   | 
db-1   | 2026-06-26 02:58:21.136 UTC [1] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 02:58:21.137 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-06-26 02:58:21.137 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1   | 2026-06-26 02:58:21.141 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 02:58:21.146 UTC [54] LOG:  database system was shut down at 2026-06-26 02:58:21 UTC
db-1   | 2026-06-26 02:58:21.154 UTC [1] LOG:  database system is ready to accept connections
db-1   | 
db-1   | PostgreSQL Database directory appears to contain a database; Skipping initialization
db-1   | 
db-1   | 2026-06-26 03:00:00.749 UTC [1] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 03:00:00.750 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-06-26 03:00:00.750 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1   | 2026-06-26 03:00:00.755 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 03:00:00.762 UTC [27] LOG:  database system was interrupted; last known up at 2026-06-26 02:58:21 UTC
db-1   | 2026-06-26 03:00:01.011 UTC [27] LOG:  database system was not properly shut down; automatic recovery in progress
db-1   | 2026-06-26 03:00:01.015 UTC [27] LOG:  redo starts at 0/170E588
db-1   | 2026-06-26 03:00:01.015 UTC [27] LOG:  invalid record length at 0/170E5C0: wanted 24, got 0
db-1   | 2026-06-26 03:00:01.015 UTC [27] LOG:  redo done at 0/170E588 system usage: CPU: user: 0.00 s, system: 0.00 s, elapsed: 0.00 s
db-1   | 2026-06-26 03:00:01.038 UTC [1] LOG:  database system is ready to accept connections
db-1   | 2026-06-26 03:00:30.945 UTC [1] LOG:  received fast shutdown request
db-1   | 2026-06-26 03:00:30.949 UTC [1] LOG:  aborting any active transactions
db-1   | 2026-06-26 03:00:30.957 UTC [1] LOG:  background worker "logical replication launcher" (PID 33) exited with exit code 1
db-1   | 2026-06-26 03:00:30.957 UTC [28] LOG:  shutting down
db-1   | 2026-06-26 03:00:30.993 UTC [1] LOG:  database system is shut down
db-1   | 
db-1   | PostgreSQL Database directory appears to contain a database; Skipping initialization
db-1   | 
db-1   | 2026-06-26 03:01:45.615 UTC [1] LOG:  starting PostgreSQL 14.23 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1   | 2026-06-26 03:01:45.615 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-06-26 03:01:45.615 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1   | 2026-06-26 03:01:45.620 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1   | 2026-06-26 03:01:45.628 UTC [27] LOG:  database system was shut down at 2026-06-26 03:00:30 UTC
db-1   | 2026-06-26 03:01:45.647 UTC [1] LOG:  database system is ready to accept connections
```

## Остановка

```bash
docker-compose down
[+] down 3/3
 ✔ Container module-05-docker-compose-app-1 Removed                                                                                                                                                                                      0.5s
 ✔ Container module-05-docker-compose-db-1  Removed                                                                                                                                                                                      0.4s
 ✔ Network module-05-docker-compose_default Removed                                                          
```

## Сборка

```bash
docker-compose build
#1 [internal] load local bake definitions
#1 reading from stdin 621B done
#1 DONE 0.0s

#2 [internal] load build definition from Dockerfile
#2 transferring dockerfile: 211B done
#2 DONE 0.0s

#3 [internal] load metadata for docker.io/library/python:3.10-slim
#3 DONE 1.2s

#4 [internal] load .dockerignore
#4 transferring context: 2B done
#4 DONE 0.0s

#5 [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a
#5 resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a 0.0s done
#5 DONE 0.0s

#6 [internal] load build context
#6 transferring context: 92B done
#6 DONE 0.0s

#7 [2/4] WORKDIR /app
#7 CACHED

#8 [3/4] COPY . .
#8 CACHED

#9 [4/4] RUN pip install -r requirements.txt
#9 CACHED

#10 exporting to image
#10 exporting layers done
#10 exporting manifest sha256:585f4b066c6228aa13d68b192d5f6462bba39bef7df85ecf22de9eba42a8d52a done
#10 exporting config sha256:5ec8001e565b949c49da6454c49d252a6b61bb71631c797d3af6ef8dcd6ea85a done
#10 exporting attestation manifest sha256:d15d6f56c93e93dde6537b1f5374b5971b3a0f35633a27dd52562945506f185e
#10 exporting attestation manifest sha256:d15d6f56c93e93dde6537b1f5374b5971b3a0f35633a27dd52562945506f185e 0.0s done
#10 exporting manifest list sha256:e1020b763c4059630bf7e14717b3e71623d10b5538c21b7b528ae0997cd36d89 0.0s done
#10 naming to docker.io/library/module-05-docker-compose-app:latest done
#10 unpacking to docker.io/library/module-05-docker-compose-app:latest 0.0s done
#10 DONE 0.1s

#11 resolving provenance for metadata file
#11 DONE 0.0s
[+] build 1/1
 ✔ Image module-05-docker-compose-app Built                                           
```