# Module 07 — CI/CD

## Что такое CI/CD

CI (Continuous Integration) - автоматическая сборка и тестирование кода
при каждом push или PR. Защищает ветку `main` от сломанного кода.
Если тесты не прошли — PR нельзя смержить.

CD (Continuous Delivery) - код автоматически подготовлен к деплою,
но деплой запускается вручную.

CD (Continuous Deployment) - деплой тоже автоматический,
без участия человека.

## Анатомия GitHub Actions

```
Workflow (.github/workflows/ci.yml)   — файл пайплайна
└── Event (on: pull_request)          — триггер запуска
   └── Job (test)                     — группа шагов
       └── Runner (ubuntu-latest)     — виртуалка GitHub где выполняется Job
           └── Step                   — одна команда или action
```

## ci.yml

```yaml
name: CI

on:
 pull_request:
   branches:
     - main

jobs:
 test:
   runs-on: ubuntu-latest

   steps:
     - name: Checkout code
       uses: actions/checkout@v4

     - name: Set up Python
       uses: actions/setup-python@v5
       with:
         python-version: "3.10"

     - name: Install dependencies
       run: pip install -r module-07-ci-cd/requirements.txt

     - name: Run tests
       run: pytest module-07-ci-cd/tests/
```

## Результат
Пайплайн запускается автоматически при создании PR в `main`.
GitHub Actions выполнил CI #1 за 14 секунд — все тесты прошли.

Ссылка на workflow run:
https://github.com/Diphenylamine/innowise-devops-internship/actions/runs/28247527256
