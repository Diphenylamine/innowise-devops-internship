# Module 08 — CD Pipeline

## Что такое Docker Registry

Docker Registry —  хранилище Docker образов типо GitHub для кода, только для образов. CI собирает образ и пушит
в Registry, сервер скачивает его оттуда и запускает.

Примеры: Docker Hub, GitHub Container Registry (GHCR), GitLab Registry.

## Настройка секретов

В GitHub репозитории добавлены секреты:
- `DOCKER_USERNAME` — логин на Docker Hub
- `DOCKER_PASSWORD` — Access Token Docker Hub

Секреты используются в workflow через `${{ secrets.DOCKER_USERNAME }}`.

## ci.yml (тесты на PR)

```yaml
name: CI

on:
  pull_request:
    branches:
      - test
      - main 

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r module-07-ci-cd/requirements.txt
      - run: pytest module-07-ci-cd/tests/
```

## cd.yml (сборка и пуш при мерже в main)

```yaml
name: CD

on:
  push:  
    branches:
      - main

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r module-07-ci-cd/requirements.txt
      - run: pytest module-07-ci-cd/tests/

  build-push:
    runs-on: ubuntu-latest
    needs: verify
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v5
        with:
          context: ./module-07-ci-cd
          push: true
          platforms: linux/amd64,linux/arm64
          tags: |
            diphenylamine/my-app:latest
            diphenylamine/my-app:${{ github.sha }}
```

## Multi-arch build

QEMU и Buildx позволяют собирать образы для нескольких архитектур:
- `linux/amd64` — Intel/AMD процессоры
- `linux/arm64` — Apple M1/M2/M3, AWS Graviton

Каждый коммит создаёт уникальный образ с тегом `github.sha`.

## Branch Protection

Ветка `main` защищена — мерж возможен только через PR без прямых пушей.
CI тесты запускаются автоматически при PR в `test` и в `main`.
Мерж возможен только после прохождения тестов.

## Ветка test и workflow

Для дополнительной защиты `main` введена промежуточная ветка `test`.

Новый флоу работы:

```
feature/* → test → main
```

1. Разработчик создаёт ветку `feature/*` и делает PR в `test`
2. CI запускает тесты автоматически
3. После прохождения тестов — мерж в `test`
4. Когда `test` стабилен — PR из `test` в `main`
5. После мержа в `main` — CD собирает образ и пушит в Docker Hub
6. `main` всегда содержит только проверенный и задеплоенный код

Это предотвращает попадание сломанного кода в `main` и даёт
дополнительный буфер для проверки перед production.

## Результат

После мержа в `main` CD автоматически собирает и пушит образ в Docker Hub.
Ссылка на образ: https://hub.docker.com/r/diphenylamine/my-app