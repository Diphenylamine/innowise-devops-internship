# Module 2 - Jenkins 101 (CI/CD Локально)

Цель модуля: развернуть Jenkins локально в Docker и настроить первый Pipeline as Code.

---

## Задача 1: Развёртывание Jenkins в Docker

**Описание:** запустить Jenkins LTS в Docker, критерий - UI доступен по `http://localhost:8080`.

**Решение:**
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins-lts
```

**Ошибка:** `pull access denied for jenkins/jenkins-lts, repository does not exist`. Образ под этим именем больше не существует.

**Как решил:** актуальный официальный образ называется `jenkins/jenkins:lts`:
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```
UI открылся на `http://localhost:8080` без проблем.

---

## Задача 2: Настройка (Getting Started)

**Описание:** получить `initialAdminPassword` через `docker logs`, установить плагины Pipeline и Git.

**Решение:**
```bash
docker logs 
```
Пароль найден в блоке со звёздочками, введён на странице "Unlock Jenkins". Выбрал **Install suggested plugins** - Pipeline и Git входят в стандартный набор. Создал администратора.

**Ошибок не было.**

---

## Задача 3: Freestyle Job

**Описание:** создать Freestyle project, Source Code Management -> Git, Execute shell -> `echo "Hello Jenkins"`, критерий - синий шар (успешная сборка).

**Решение:** New Item -> Freestyle project -> Git URL репозитория -> Build Steps -> Execute shell.

**Ошибок не было.**

---

## Задача 4: Теория "Pipeline as Code"

**Описание:** понять разницу между Freestyle (UI) и Pipeline as Code (Jenkinsfile в репозитории).

**Решение:** Freestyle хранит конфигурацию внутри самого Jenkins (XML в `jenkins_home`) - нет версий, не проходит через PR-ревью, теряется вместе с сервером. Pipeline as Code хранит "рецепт" сборки в `Jenkinsfile` рядом с кодом - история изменений видна через `git log`, конфигурация путешествует вместе с репозиторием на любой Jenkins.

---

## Задача 5: Создание Jenkinsfile

**Описание:** создать декларативный `Jenkinsfile` со stage `Test`, выполняющим `pytest`.

**Решение:** вместо заглушки взял реальное FastAPI-приложение с тестами из `module-07-ci-cd` Basic Track - скопировал `app.py`, `requirements.txt`, `tests/` в `resources/python/`.

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                dir('pro-track/module-02-jenkins/resources/python') {
                    sh 'pip install -r requirements.txt'
                    sh 'pytest'
                }
            }
        }
    }
}
```

**Ошибок не было на этом шаге** - все проблемы всплыли позже, при реальном запуске в задаче 6.

---

## Задача 6: Pipeline Job (Pipeline script from SCM)

**Описание:** создать Job типа Pipeline, указать Git URL и путь к Jenkinsfile, критерий - Jenkins клонирует репо, находит Jenkinsfile, запускает pytest.

**Решение:** New Item -> Pipeline -> Definition: Pipeline script from SCM -> Git URL -> Script Path.

**Ошибка 1:**
pip: not found
Базовый образ `jenkins/jenkins:lts` не содержит Python - ни интерпретатора, ни pip.

**Как решил (временно):** зашёл в контейнер и поставил Python вручную:
```bash
docker exec -u root -it <container_id> bash
apt-get update && apt-get install -y python3 python3-pip python3-venv
```

**Ошибка 2:** это временное решение не пережило бы пересоздание контейнера. Решил закрепить Python в образе через собственный `Dockerfile.jenkins` с multi-stage сборкой (venv собирается в стадии `python:3.13-slim`, копируется в финальный `jenkins/jenkins:lts`).

Первая версия дала:
pip install -r requirements.txt
error: externally-managed-environment
PEP 668 блокирует `pip install` напрямую в системный Python современных Debian-образов.

**Ошибка 3:** после multi-stage сборки снова:
pip: not found
Диагностика показала:
```bash
docker exec -u jenkins <container> ls -la /opt/venv/bin/python3
lrwxrwxrwx ... python3 -> /usr/local/bin/python3
```
`/opt/venv/bin/python3` - символическая ссылка на путь из другого базового образа (`python:3.13-slim`, где Python лежит в `/usr/local/bin/`), которого физически нет во второй стадии (`jenkins/jenkins:lts`, где `apt`-python лежит в `/usr/bin/`). Venv не переносим между разными базовыми образами "как есть" - он содержит абсолютные пути к оригинальному интерпретатору.

**Как решил:** пересобрал обе стадии `Dockerfile.jenkins` на одной и той же базе (`jenkins/jenkins:lts` в обеих стадиях, просто с разным набором установленных пакетов). Пути внутри venv совпали, симлинки перестали быть битыми.

**Финал:** `docker-compose.yml` + `Dockerfile.jenkins` (multi-stage, единая база), пересобрал контейнер с нуля, пересоздал джобу - pytest успешно выполнился:
tests/test_app.py .    [100%]
1 passed, 1 warning in 0.34s
Finished: SUCCESS

---

## Задача 7: Docker-in-Docker

**Описание:** дать Jenkins-контейнеру доступ к Docker хоста через проброс `docker.sock`, критерий - `sh 'docker ps'` выполняется успешно внутри Jenkinsfile.

**Решение:** отдельные файлы `v2.Dockerfile.jenkins` (добавлен `docker-ce-cli` через официальный APT-репозиторий Docker) и `v2.docker-compose.yml` с проброшенным сокетом:
```yaml
volumes:
  - jenkins_home_v2:/var/jenkins_home
  - /var/run/docker.sock:/var/run/docker.sock
```

**Ошибка:**
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
Сокет на хосте принадлежит группе `docker` (GID нужно узнавать явно - на разных машинах отличается). Пользователь `jenkins` внутри контейнера - обычный, непривилегированный, не входит в эту группу.

**Как решил:**
```bash
getent group docker
# docker:x:1001:usr
```
Добавил в `v2.Dockerfile.jenkins` создание группы с тем же GID и добавление в неё пользователя `jenkins`:
```dockerfile
groupadd -g 1001 dockerhost && \
usermod -aG dockerhost jenkins
```
После пересборки - `docker ps` внутри контейнера успешно показал список хостовых контейнеров, включая сам Jenkins.

---

## Задача 8: Сборка образа (stage Build Image)

**Описание:** добавить stage, который собирает Docker-образ приложения с тегом `${BUILD_NUMBER}`.

**Решение:** отдельный `v3.Jenkinsfile` с двумя stages (Docker Check + Build Image), скопировал `Dockerfile` приложения из `module-07-ci-cd`.

После коммита и запуска:
Successfully built 3a1763beba49
Successfully tagged my-app-jenkins:1
Finished: SUCCESS

---

## Задача 9: Multibranch Pipeline

**Описание:** создать Multibranch Pipeline Job, критерий - Jenkins находит `main` и `feature/` ветки.

**Решение:** New Item -> Multibranch Pipeline -> Branch Source: Git -> Build Configuration -> Script Path.

После сканирования:
Checking branch feature/ProTrack-module-02-jenkins
'pro-track/module-02-jenkins/resources/v3.Jenkinsfile' found
Met criteria
Processed 20 branches
Finished: SUCCESS
Jenkins корректно проверил все 20 веток (включая `main` и множество `feature/*`), нашёл единственную ветку с подходящим Jenkinsfile, создал под-pipeline, сборка внутри неё прошла успешно.

---

## Задача 10: Credentials и безопасная публикация

**Описание:** добавить `DOCKER_USERNAME`/`DOCKER_PASSWORD` в Jenkins Credentials, использовать `withCredentials` в Jenkinsfile, критерий - пайплайн пушит образ в Docker Hub, не светя пароль в логах.

**Решение:**

Создал новый Docker Hub Access Token, добавил в Jenkins: Manage Jenkins -> Credentials -> Add Credentials -> Kind: Username with password -> ID: `docker-hub-credentials`.

`v4.Jenkinsfile`:
```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "diphenylamine/my-app-jenkins"
    }

    stages {
        stage('Build Image') {
            steps {
                dir('pro-track/module-02-jenkins/resources/python') {
                    sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
                }
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}'
                }
            }
        }
    }
}
```

Ключевой момент безопасности - `--password-stdin` вместо передачи пароля как аргумента командной строки (иначе он был бы виден в `ps aux` на хосте).

Результат:
echo ****
Masking supported pattern matches of $DOCKER_PASS
docker login -u diphenylamine --password-stdin
Login Succeeded
docker push diphenylamine/my-app-jenkins:1
1: digest: sha256:3a1763beba4985...
Finished: SUCCESS

Jenkins автоматически заменил `$DOCKER_PASS` на `****` даже в самой печатаемой команде - пароль нигде не появился в открытом виде.
