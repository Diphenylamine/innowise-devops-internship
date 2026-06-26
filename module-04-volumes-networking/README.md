# Module 4: Docker Storage (Volumes) и Networking

## Эфемерность данных контейнера

```bash
docker run -it ubuntu bash
```

```
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
107e4f1717f2: Download complete
Digest: sha256:53958ec7b67c2c9355df922dd08dbf0360611f8c3cdb656875e81873db9ffdba
Status: Downloaded newer image for ubuntu:latest
```

Внутри контейнера
```bash
mkdir /data
touch /data/test.txt
root@f27e392aad95:/# ls /data
test.txt
root@f27e392aad95:/# exit
exit
```

Узнаем ID контейнера

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE      COMMAND                  CREATED              STATUS                      PORTS                    NAMES
f27e392aad95   ubuntu     "bash"                   About a minute ago   Exited (0) 44 seconds ago                            distracted_satoshi
```

Удаляем контейнер

```bash
docker rm f27e392aad95
```

Заново запускаем контейнер и проверяем директорию data


```bash
docker run -it ubuntu bash
root@4aead0725b8a:/# ls /data
ls: cannot access '/data': No such file or directory
```

Файл `/data/test.txt` исчез вместе с контейнером.
Файловая система контейнера эфемерна — при удалении контейнера все данные внутри него удаляются безвозвратно.

## Bind Mount vs Volume

### Bind Mount
```
┌─────────────────────────────────────────────────────┐
│                      Хост                           │
│                                                     │
│   /home/user/myapp   ←──────────────────────────┐   │
│                                                 │   │
└─────────────────────────────────────────────────│───┘
                                                  │
                                              синхронизация
                                                  │
┌─────────────────────────────────────────────────│───┐
│                   Контейнер                     │   │
│                                                 │   │
│   /app  ────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
Указываем папку на хосте → она монтируется в контейнер
Изменения видны сразу с обеих сторон (hot-reload)
```

### Volume
```
┌─────────────────────────────────────────────────────┐
│                      Хост                           │
│                                                     │
│   /var/lib/docker/volumes/postgres-data  ───────┐   │
│   (Docker управляет этой папкой)                │   │
└─────────────────────────────────────────────────│───┘
                                                  │
                                              монтирование
                                                  │
┌─────────────────────────────────────────────────│───┐
│                   Контейнер                     │   │
│                                                 │   │
│   /var/lib/postgresql/data  ────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
Docker сам управляет хранилищем
Данные живут даже после удаления контейнера
```

## Bind Mount

Bind Mount позволяет монтировать папку с хоста в контейнер.
Изменения файлов на хосте сразу видны внутри контейнера.

```bash
docker run -d -p 5000:5000 -v ${PWD}:/app my-app:1.0 uvicorn app:app --host 0.0.0.0. --port 5000 --reload 
```

python до изменений
```python
    from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет!. "}
```

Ответ от браузера:

```json
{"message": "Привет!"}
```

python после изменений
```python
    from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет!. hot-realod "}
```

Ответ от браузера:

```json
{"message": "Привет! hot-reload"}
```

## Volume

Volume — это механизм хранения данных которым управляет Docker.
В отличие от файловой системы контейнера, данные в Volume сохраняются
после остановки и удаления контейнера. Docker хранит Volume на хосте
в `/var/lib/docker/volumes/`.

Используется для: баз данных, файлов которые должны пережить контейнер.

```bash
docker volume create pg-learn-data
```

```
pg-learn-data
```

ВАЖНО!!!
Вместо postgres-data было создано pg-learn-data из-за конфликта с существующим проектом

```bash
docker run -d -p 5432:5432 -v pg-learn-data:/var/lib/postgresql -e POSTGRES_PASSWORD=mysecret postgres
docker ps

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS                                         NAMES
4dc5edf3110d   postgres     "docker-entrypoint.s…"   5 seconds ago    Up 5 seconds    0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   jovial_leakey
```

Cоздадим базу данных для проверки

```bash
docker exec -it 4dc5edf3110d bash
psql -U postgres
CREATE DATABASE testdb;
\l

                                               List of databases
   Name    |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | Locale | ICU Rules |   Access privileges
-----------+----------+----------+-----------------+------------+------------+--------+-----------+-----------------------
 postgres  | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
 template0 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
 testdb    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
(4 rows)

\q
exit
```

Останавливаем и удаляем контейнер
```bash
docker stop 4dc5edf3110d
docker rm 4dc5edf3110d
```

Заново запускаем контейнер и проверяем сохранилась ли база

```bash
docker run -d -p 5432:5432 -v pg-learn-data:/var/lib/postgresql -e POSTGRES_PASSWORD=mysecret postgres
docker ps

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS                                         NAMES
2a65baee69c7   postgres     "docker-entrypoint.s…"   34 seconds ago   Up 33 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   modest_jepsen

docker exec -it 2a65baee69c7 bash
psql -U postgres
\l

                                               List of databases
   Name    |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | Locale | ICU Rules |   Access privileges
-----------+----------+----------+-----------------+------------+------------+--------+-----------+-----------------------
 postgres  | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
 template0 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
 testdb    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
(4 rows)

\q
exit
```

Видно что созданная база данных сохранилась, что показывает что volume работает корректно

## Network bridge & DNS

В стандартной сети bridge контейнеры общаются только по IP — это неудобно
так как IP меняется при перезапуске. В кастомной сети Docker обеспечивает
DNS — контейнеры находят друг друга по имени. Именно поэтому приложение
подключается к БД как `pg-db:5432`, а не `172.18.0.2:5432`.

Запускаем 2 ubuntu контейнера и узнаем их ip
```bash
docker run -d --name ubuntu1 ubuntu sleep 1000
docker run -d --name ubuntu2 ubuntu sleep 1000

docker inspect ubuntu1 | findstr IPAddress
 "IPAddress": "172.17.0.4"

docker inspect ubuntu2 | findstr IPAddress
 "IPAddress": "172.17.0.5"
```

Входим в контейнер, устанавливаем iputils

```bash
docker exec -it ubuntu1 bash
apt-get update && apt-get install -y iputils-ping
```

Проверяем видимость контейнера ubuntu2 из ubuntu1
```bash
ping 172.17.0.5

PING 172.17.0.5 (172.17.0.5) 56(84) bytes of data.
64 bytes from 172.17.0.5: icmp_seq=1 ttl=64 time=0.340 ms
64 bytes from 172.17.0.5: icmp_seq=2 ttl=64 time=0.067 ms
64 bytes from 172.17.0.5: icmp_seq=3 ttl=64 time=0.066 ms
64 bytes from 172.17.0.5: icmp_seq=4 ttl=64 time=0.103 ms
64 bytes from 172.17.0.5: icmp_seq=5 ttl=64 time=0.077 ms
64 bytes from 172.17.0.5: icmp_seq=6 ttl=64 time=0.067 ms
--- 172.17.0.5 ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 4997ms
rtt min/avg/max/mdev = 0.066/0.120/0.340/0.099 ms

exit
```

ping проходит, это значит что контейнеры видят друг друга

Создаем свою bridge сеть:

```bash
docker network create my-app-net
docker network ls

NETWORK ID     NAME         DRIVER    SCOPE
1e280a231295   my-app-net   bridge    local
```

Сеть создана. Теперь запускаем Postgres в этой сети:

```bash
docker run -d --network my-app-net --name pg-db -e POSTGRES_PASSWORD=mysecret postgres
docker ps

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS                                         NAMES
63d8b5b757c0   postgres     "docker-entrypoint.s…"   8 seconds ago    Up 7 seconds    5432/tcp                                      pg-db
acf6df9f4906   ubuntu       "sleep 1000"             3 minutes ago    Up 3 minutes                                                  ubuntu2
f7d29c9ea99e   ubuntu       "sleep 1000"             3 minutes ago    Up 3 minutes                                                  ubuntu1
```

Запускаем еще один контейнер в этой сети

```bash
docker run -it --network my-app-net ubuntu bash
```

Внутри контейнера проверим как работает DNS

```bash
apt-get update && apt-get install -y iputils-ping
ping pg-db

PING pg-db (172.18.0.2) 56(84) bytes of data.
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=1 ttl=64 time=0.287 ms
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=2 ttl=64 time=0.082 ms
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=3 ttl=64 time=0.079 ms
--- pg-db ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 1998ms
rtt min/avg/max/mdev = 0.079/0.149/0.287/0.097 ms

root@1e2c46e17988:/# exit
```

Мы видим 64 bytes from pg-db.my-app-net (172.18.0.2). Мы делаем ping по имени pg-db — не по ip. Это означает что DNS работает корректно.