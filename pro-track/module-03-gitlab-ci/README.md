# Pro Track - Модуль 3: GitLab CI (Локальное развёртывание)

## Задача 1: Развёртывание GitLab

**Описание:** поднять GitLab EE в Docker через docker-compose. Критерий - UI доступен в браузере.

**Решение:**

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ee:latest
    hostname: 'localhost'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://localhost:8090'
    ports:
      - "8090:8090"
      - "10443:443"
      - "10022:22"
    volumes:
      - gitlab_config:/etc/gitlab
      - gitlab_logs:/var/log/gitlab
      - gitlab_data:/var/opt/gitlab
    shm_size: '256m'

  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    volumes:
      - gitlab_runner_config:/etc/gitlab-runner
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  gitlab_config:
  gitlab_logs:
  gitlab_data:
  gitlab_runner_config:
```

Порт в `ports` и в `external_url` совпадает (`8090:8090`, а не `8090:80`) - это принципиально: GitLab при кастомном порте в `external_url` переключает внутренний nginx слушать именно этот порт, а не `80`, что подтверждено официальным примером конфигурации GitLab для нестандартного порта.

```bash
docker-compose up -d
docker ps
curl -I http://localhost:8090
```

Вывод (проверка доступности):

HTTP/1.1 302 Found
Server: nginx
Date: Tue, 18 Aug 2026 01:07:27 GMT
Content-Type: text/html; charset=utf-8
Location: http://localhost:8090/users/sign_in
X-Gitlab-Meta: {"correlation_id":"01M096HDF2B3A4JR25MP6MP6RZ","version":"1"}
...

---

## Задача 2: Настройка

**Описание:** войти под `root`, создать проект, запушить приложение (FastAPI + pytest) под именем `my-app`.

**Решение:**

Получение пароля:
```bash
docker exec -it module-03-gitlab-ci-gitlab-1 grep 'Password:' /etc/gitlab/initial_root_password
```

Password: DZpH0kr+73W6k6/ubu0z6vneKihpEJ5R3rwAk+kqVuk=


Проект `my-app` создан через UI (**New project → Create blank project**, Private).

Инициализация и push:
```bash
cd .../resources
rm -rf .git
git init
git branch -M main
git remote add origin http://localhost:8090/root/my-app.git
git add .
git commit -m "Initial commit: FastAPI app with tests"
git push -u origin main --force
```

Вывод:

Enumerating objects: 9, done.
Writing objects: 100% (9/9), 1.16 KiB | 42.00 KiB/s, done.
To http://localhost:8090/root/my-app.git

b51a2cf...1c8fcfd main -> main (forced update)
branch 'main' set up to track 'origin/main'.

---

## Задача 3: Развёртывание Runner

**Описание:** запустить GitLab Runner в Docker.

**Решение:** Runner поднят как сервис в том же `docker-compose.yml`, что и GitLab (см. задачу 1) - функционально идентично отдельному `docker run`, отличие организационное.

```bash
docker ps | grep runner
```

d76a0c2a3906 gitlab/gitlab-runner:latest "/usr/bin/dumb-init …" 16 minutes ago Up 16 minutes module-03-gitlab-ci-gitlab-runner-1

---

## Задача 4: Регистрация Runner

**Описание:** зарегистрировать Runner в GitLab. Критерий - Runner виден в UI (Settings → CI/CD → Runners).

**Решение:**

В UI: **Settings → CI/CD → Runners → Create project runner**, тег `docker`, галочка **Run untagged jobs**.

Регистрация через `docker exec` с `--url http://gitlab:8090` (не `localhost` из подсказки UI - Runner в отдельном контейнере, обращается к GitLab через docker-сеть по имени сервиса):

```bash
docker exec -it module-03-gitlab-ci-gitlab-runner-1 gitlab-runner register \
  --url http://gitlab:8090 \
  --token glrt-adapf_Vog6JuXLqjjV7YVG86MQpwOjEKdDozCnU6MQ8.01.170np604z \
  --executor docker \
  --docker-image docker:latest \
  --non-interactive
```

Вывод:

Runtime platform arch=amd64 os=linux pid=55 revision=343288f1 version=19.2.2
Running in system-mode.
Verifying runner... is valid correlation_id=01M097MJJH92EQ9YJKBB4ZTAZE runner=adapf_Vog runner_name=d76a0c2a3906
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!
Configuration (with the authentication token) was saved in "/etc/gitlab-runner/config.toml"

---

## Задача 5: `.gitlab-ci.yml`

**Описание:** создать `.gitlab-ci.yml` в корне `my-app` со stages `[test, build]`.

**Решение:**

```yaml
stages:
  - test
  - build
```

```toml
[[runners]]
  url = "http://gitlab:8090"
  clone_url = "http://gitlab:8090"
  ...
  [runners.docker]
    network_mode = "module-03-gitlab-ci_default"
    privileged = true
```

```bash
docker exec module-03-gitlab-ci-gitlab-runner-1 cat /etc/gitlab-runner/config.toml
```

[[runners]]
name = "d76a0c2a3906"
url = "http://gitlab:8090"
clone_url = "http://gitlab:8090"
...
executor = "docker"
...
[runners.docker]
network_mode = "module-03-gitlab-ci_default"
tls_verify = false
image = "docker:latest"
privileged = true
...

---

## Задача 6: job `test`

**Описание:** описать job `test` (pip install + pytest). Критерий — git push → Runner подхватывает job → тесты проходят.

**Решение:**

```yaml
test:
  stage: test
  image: python:3.10-slim
  script:
    - pip install -r requirements.txt
    - pytest
```

```bash
git add .gitlab-ci.yml
git commit -m "ci: Add .gitlab-ci.yml with test stage"
git push
```

Лог выполненного job:

Checking out 1ab44065 as detached HEAD (ref is main)...
$ pip install -r requirements.txt
Successfully installed annotated-doc-0.0.5 ... fastapi-0.141.1 ... pytest-9.1.1 ...
$ pytest
============================= test session starts ==============================
platform linux -- Python 3.10.21, pytest-9.1.1, pluggy-1.6.0
rootdir: /builds/root/my-app
plugins: anyio-4.14.2
collected 1 item
tests/test_app.py . [100%]
========================= 1 passed, 1 warning in 0.28s =========================
Cleaning up project directory and file based variables
Job succeeded

## Задача 7: Docker-in-Docker

**Описание:** понять и настроить механизм DinD - Runner запускает `docker:dind` как "братский" контейнер-сервис.

**Решение:** DinD требует `privileged = true` в `config.toml` Runner'а - без него Docker-демон внутри сервиса `docker:dind` не может создавать вложенные контейнеры. 

```bash
docker exec module-03-gitlab-ci-gitlab-runner-1 grep privileged /etc/gitlab-runner/config.toml
    privileged = true
```
---

## Задача 8: job `build`

**Описание:** описать job `build` с `image: docker:latest` + `services: [docker:dind]`, логин и push в Registry через встроенные CI-переменные.

**Решение:**

```yaml
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build --provenance=false -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```



$ docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
Login Succeeded

**Описание:** включить встроенный Docker Registry в GitLab. Критерий - пайплайн (задача 8) пушит образ во внутренний Registry.

**Решение:**

Добавлено в `docker-compose.yml`:
```yaml
environment:
  GITLAB_OMNIBUS_CONFIG: |
    external_url 'http://localhost:8090'
    registry_external_url 'http://localhost:5050'
ports:
  - "8090:8090"
  - "10443:443"
  - "10022:22"
  - "5050:5050"
```

```bash
docker-compose up -d gitlab
curl -I http://localhost:5050
```

HTTP/1.1 200 OK
Server: nginx
Cache-Control: no-cache
Strict-Transport-Security: max-age=63072000

---