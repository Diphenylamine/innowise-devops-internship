# Module 1 - Docker Hardening (Security & Optimization)

Цель модуля: перейти от Dockerfile который "просто работает" к безопасному и оптимизированному.

---

## Задача 1: Анализ Dockerfile через hadolint

**Описание:** установить hadolint, написать "плохой" Dockerfile (раздельные `apt update`/`apt install`), проанализировать.

**Решение:**

```bash
sudo wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
sudo chmod +x /usr/local/bin/hadolint
```

`Dockerfile.bad`:
```dockerfile
FROM python:3.8-slim-buster
WORKDIR /app
RUN apt update
RUN apt install -y curl
COPY . .
RUN pip install -r requirements.txt
CMD python app.py
```

```bash
hadolint Dockerfile.bad
```

Найдено 6 проблем: `DL3009` (apt lists не удалены), `DL3027` x2 (apt вместо apt-get), `DL3059` (дублирующиеся RUN), `DL3042` (pip без --no-cache-dir), `DL3025` (CMD в shell-форме).

**Ошибок не было**.

---

## Задача 2: Слияние RUN-слоёв

**Описание:** объединить `apt update`/`apt install` через `&&`, критерий - hadolint больше не ругается, `docker history` показывает меньше слоёв.

**Решение:**

```dockerfile
FROM python:3.8-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl=<версия> && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```

При первой сборке возникла отдельная проблема:

**Ошибка:** `404 Not Found` при `apt-get update` - репозитории Debian Buster архивированы, `deb.debian.org` больше не отдаёт пакеты для EOL-версии.

**Решение:** добавил переключение на архивный репозиторий:
```dockerfile
RUN sed -i 's/deb.debian.org/archive.debian.org/g; s|security.debian.org|archive.debian.org/debian-security|g' /etc/apt/sources.list
```

Проверка `docker history` подтвердила: слои `apt update` + `apt install` (было 2 слоя) объединились в 1, размер тоже сократился.

---

## Задача 3: Сканирование уязвимостей (Trivy)

**Описание:** установить Trivy, просканировать образ на `python:3.8-slim-buster`.

**Решение:**

```bash
sudo apt-get install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install -y trivy
trivy image my-app:bad
```

**Результат:** Total 129 CVE в ОС-слое (2 CRITICAL, 42 HIGH) + 17 в Python-пакетах. Оба CRITICAL (`libdb5.3`, `zlib1g`) помечены `will_not_fix` - Debian Buster вышел из поддержки.

**Ошибок не было**.

---

## Задача 4: Пересборка на новый образ, 0 HIGH/CRITICAL

**Описание:** пересобрать на `python:3.11-slim-bullseye`, критерий - `trivy image my-app:2.0` показывает 0 HIGH/CRITICAL.

**Решение (итоговое):**

```dockerfile
FROM python:3.11-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt
CMD ["python", "app.py"]
```

**Проблема:** пересборка на `bullseye` дала 72+3 CVE (8 CRITICAL, 64 HIGH) - критерий не выполнен. Попробовал `bookworm` - 39+2 CVE (4 CRITICAL, 35 HIGH) - тоже не выполнен. Даже актуальный на момент теста Debian уже накопил неисправленные CVE (дистрибутив стареет быстрее, чем ожидалось).

**Как решил:** перешёл с Debian на Alpine (`python:3.11-alpine`) - OS-слой сразу дал 0 уязвимостей. Остались 2 HIGH в транзитивных зависимостях setuptools (`jaraco.context`, `wheel`).

**Финальный фикс:** явный апгрейд `pip install --upgrade pip setuptools wheel` перед установкой зависимостей - подтянул пропатченные версии вендоренных пакетов. Итог: **0 HIGH/CRITICAL** во всём образе.

---

## Задача 5: Теория BuildKit

**Описание:** включить BuildKit (`DOCKER_BUILDKIT=1`), пересобрать образ, критерий - вывод стал "древовидным".

**Решение:** BuildKit в Docker 29.x включён по умолчанию без явной переменной - все сборки уже показывали графовый вывод (`=> [1/5] FROM ...`). Для контраста явно отключил через `DOCKER_BUILDKIT=0` - получил вывод legacy builder (`Step 1/6 : FROM ...`) с предупреждением о скором удалении legacy builder.

**Ошибок не было** - задача теоретическая, современная версия Docker уже даёт нужное поведение "из коробки".

---

## Задача 6: BuildKit cache mount

**Описание:** заменить `RUN pip install ...` на `RUN --mount=type=cache,target=/root/.cache/pip pip install ...`, критерий - повторная сборка (даже после `docker builder prune`) использует кэш pip.

**Решение:**
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt
```

**Проблема:** первая проверка эффекта была некорректной - второй `docker build` без изменений показал `CACHED` для всего шага целиком (обычный layer cache), это не доказывало работу именно cache mount.

**Как решил:** сделал строгий тест - изменил `app.py`, собрал с `--progress=plain --no-cache=false`. Слой `RUN` пересобрался с нуля (не `CACHED`), но в построчном логе pip показал `Using cached ...` для всех 19 пакетов - кэш-том пережил инвалидацию слоя и даже предварительную `docker builder prune -af` (очистившую 8.4 ГБ layer cache).

---

## Задача 7: Multi-arch build

**Описание:** установить qemu и buildx, собрать образ под `linux/amd64,linux/arm64`, запушить в Docker Hub.

**Решение:**
```bash
docker buildx create --name multiarch-builder --use
docker buildx inspect --bootstrap
docker login
docker buildx build --platform linux/amd64,linux/arm64 \
  -t diphenylamine/my-app-hardened:2.0 -f Dockerfile.v3 --push .
docker buildx imagetools inspect diphenylamine/my-app-hardened:2.0
```

**Результат:** `imagetools inspect` подтвердил наличие `Platform: linux/amd64` и `Platform: linux/arm64` в едином манифесте.

**Ошибок не было**.

---

## Задача 8: Build secrets

**Описание:** изучить `RUN --mount=type=secret,id=mysecret`, критерий - секрет используется при сборке, но не сохраняется в слоях образа.

**Решение:**
```dockerfile
RUN --mount=type=secret,id=mysecret \
    cat /run/secrets/mysecret
```
```bash
docker build --secret id=mysecret,src=secret_token.txt -t my-app:4.0 -f Dockerfile.v4 .
```

**Найденный баг:** первая проверка через `grep -r 'токен' /app /usr /etc /root` внутри контейнера нашла секрет - но не через сам механизм `--mount=type=secret` (он отработал правильно), а потому что файл `secret_token.txt` лежал в той же директории что и Dockerfile и попал в образ через обычный `COPY . .`. Он был добавлен в `.gitignore`, но не в `.dockerignore`.

**Решение:** добавил `secret_token.txt` в `.dockerignore`, пересобрал с `--no-cache`. Повторная проверка - `NOT FOUND`, секрет нигде не осел в образе.

---

## Задача 9: Distroless-образ (Java)

**Описание:** написать multi-stage Dockerfile, финальный образ - distroless, критерии (для Go) - `< 20 МБ`, `bash` не работает.

**Решение (выбрал Java вместо Go):**
```dockerfile
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app
COPY Main.java .
RUN javac Main.java && \
    echo "Main-Class: Main" > manifest.txt && \
    jar cfm app.jar manifest.txt Main.class

FROM gcr.io/distroless/java17-debian12
WORKDIR /app
COPY --from=builder /app/app.jar .
CMD ["app.jar"]
```

**ВАЖНО:** критерий `< 20 МБ` физически недостижим для Java (нужен минимум JRE) -  значит, что для Java этот критерий не выполним, остаётся только проверка отсутствия shell.

**Ошибка 1:** `CMD ["-cp", ".", "Main"]` с обычным `.class`-файлом дал `Error: Unable to access jarfile Main`.

**Расследование:** `docker inspect gcr.io/distroless/java17-debian12:latest` показал `Entrypoint: [/usr/bin/java -jar]` - жёстко зашитый, не переопределяемый через `CMD`. Любой `CMD` только дописывается как аргумент к `java -jar`.

**Решение:** пересобрал `.class` в полноценный `.jar` через `jar cfm`, `CMD ["app.jar"]` - заработало (`Hello from distroless!`).

**Ошибка 2:** проверка отсутствия shell через `docker run my-app bash` дала не ту ошибку что ожидалась (`Unable to access jarfile bash` вместо `not found`) - из-за того же жёсткого ENTRYPOINT, `bash` интерпретировался как имя jar-файла, а не как попытка запуска.

**Решение:** правильный тест - переопределить сам ENTRYPOINT явно:
```bash
docker run --rm --entrypoint bash my-app:distroless-java
docker run --rm --entrypoint sh my-app:distroless-java
```
Оба дали `exec: "bash"/"sh": executable file not found in $PATH` - подтверждение отсутствия shell в образе.

---

## Задача 10: Docker Compose Override (dev vs prod)

**Описание:** `docker-compose.yml` (prod, `image:`) + `docker-compose.override.yml` (dev, `build:` + `volumes:`), критерий - `docker-compose up` запускает dev, `docker-compose -f docker-compose.yml up` запускает prod.

**Решение:**

`docker-compose.yml`:
```yaml
services:
  app:
    image: diphenylamine/my-app-hardened:2.0
    ports:
      - "5000:5000"
```

`docker-compose.override.yml`:
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.v3
    volumes:
      - .:/app
```

**Проблема:** первый `docker-compose up` показал `Image ... Pulled` вместо ожидаемого `Building` - казалось что override не подхватился.

**Расследование:** `docker-compose config` показал корректно смёрженный конфиг (и `build:`, и `image:` присутствовали одновременно) - override реально работал, но Compose предпочёл уже закэшированный локально `image`, не пересобирая.

**Решение:** `docker-compose up --build` явно форсировал пересборку - `Image ... Built`, критерий 1 выполен.

Для критерия 2 первая проверка `-f docker-compose.yml up` тоже дала смазанный результат (`Recreated` без явного `Pulled`/`Built`) - Compose переиспользовал существующий контейнер. Сделал чистый тест: `docker-compose down` + `docker rmi diphenylamine/my-app-hardened:2.0`, затем `docker-compose -f docker-compose.yml up` - получил чистое `Image ... Pulled`, критерий 2 выполен.
