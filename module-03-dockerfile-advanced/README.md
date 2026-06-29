# Module 03 — Dockerfile Advanced

## Кэширование слоёв

### Проблема

При использовании `COPY . .` до `RUN pip install` — любое изменение в коде сбрасывает кэш и зависимости устанавливаются заново.

#### dockerfile до оптимизации

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### app.py до изменений

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет!"}
```

#### Вывод Сборки до изменений в app.py

```
[+] Building 10.7s (9/9) FINISHED                                                                                                           docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.1s
 => => transferring dockerfile: 211B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                         1.0s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => [internal] load build context                                                                                                           0.0s
 => => transferring context: 1.38kB                                                                                                         0.0s
 => CACHED [2/4] WORKDIR /app                                                                                                               0.0s
 => [3/4] COPY . .                                                                                                                          0.0s
 => [4/4] RUN pip install -r requirements.txt                                                                                               8.3s
 => exporting to image                                                                                                                      1.8s
 => => exporting layers                                                                                                                     1.1s
 => => exporting manifest sha256:d8328d541d5f5735edc81ab8979aeae2a70006c052a2f0393490babca5acd1f7                                           0.0s
 => => exporting config sha256:4ce0586bf5f140186d8682ec5c319004fccbf039ac738db1413f3f7c66f27978                                             0.0s
 => => exporting attestation manifest sha256:68f04963e21fdba7ff4b97b48c03a2665167374b6838ac6ae97e273f803cf42d                               0.0s
 => => exporting manifest list sha256:eba38da6fd9ce0d6156a6e9df4475753e2e4b44ae6dec35b39adc49cbc2aa037                                      0.0s
 => => naming to docker.io/library/my-app:1.0                                                                                               0.0s
 => => unpacking to docker.io/library/my-app:1.0                                                                                            0.7s

```

#### app.py после изменений

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет! Версия 2"}
```

#### Вывод Сборки после изменения в app.py

```
[+] Building 11.5s (9/9) FINISHED                                                                                                           docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.1s
 => => transferring dockerfile: 211B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                         1.0s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => [internal] load build context                                                                                                           0.0s
 => => transferring context: 1.38kB                                                                                                         0.0s
 => CACHED [2/4] WORKDIR /app                                                                                                               0.0s
 => [3/4] COPY . .                                                                                                                          0.0s
 => [4/4] RUN pip install -r requirements.txt                                                                                               8.3s
 => exporting to image                                                                                                                      1.8s
 => => exporting layers                                                                                                                     1.1s
 => => exporting manifest sha256:d8328d541d5f5735edc81ab8979aeae2a70006c052a2f0393490babca5acd1f7                                           0.0s
 => => exporting config sha256:4ce0586bf5f140186d8682ec5c319004fccbf039ac738db1413f3f7c66f27978                                             0.0s
 => => exporting attestation manifest sha256:68f04963e21fdba7ff4b97b48c03a2665167374b6838ac6ae97e273f803cf42d                               0.0s
 => => exporting manifest list sha256:eba38da6fd9ce0d6156a6e9df4475753e2e4b44ae6dec35b39adc49cbc2aa037                                      0.0s
 => => naming to docker.io/library/my-app:1.0                                                                                               0.0s
 => => unpacking to docker.io/library/my-app:1.0                                                                                            0.7s

```

### Оптимизация

#### dockerfile после оптимизации

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### app.py до изменений

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет! Версия 3"}
```

#### Вывод Сборки до изменений в app.py

```
[+] Building 10.7s (9/9) FINISHED                                                                                                           docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.1s
 => => transferring dockerfile: 211B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                         1.0s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => [internal] load build context                                                                                                           0.0s
 => => transferring context: 1.38kB                                                                                                         0.0s
 => CACHED [2/4] WORKDIR /app                                                                                                               0.0s
 => [3/4] COPY . .                                                                                                                          0.0s
 => [4/4] RUN pip install -r requirements.txt                                                                                               8.3s
 => exporting to image                                                                                                                      1.8s
 => => exporting layers                                                                                                                     1.1s
 => => exporting manifest sha256:d8328d541d5f5735edc81ab8979aeae2a70006c052a2f0393490babca5acd1f7                                           0.0s
 => => exporting config sha256:4ce0586bf5f140186d8682ec5c319004fccbf039ac738db1413f3f7c66f27978                                             0.0s
 => => exporting attestation manifest sha256:68f04963e21fdba7ff4b97b48c03a2665167374b6838ac6ae97e273f803cf42d                               0.0s
 => => exporting manifest list sha256:eba38da6fd9ce0d6156a6e9df4475753e2e4b44ae6dec35b39adc49cbc2aa037                                      0.0s
 => => naming to docker.io/library/my-app:3.0                                                                                               0.0s
 => => unpacking to docker.io/library/my-app:3.0                                                                                            0.7s

```

#### app.py после изменений

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет! Версия 4"}
```

#### Вывод Сборки после изменения в app.py

```
[+] Building 0.6s (10/10) FINISHED                                                                                              docker:default
 => [internal] load build definition from Dockerfile                                                                            0.0s
 => => transferring dockerfile: 238B                                                                                            0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                             0.3s
 => [internal] load .dockerignore                                                                                               0.0s
 => => transferring context: 107B                                                                                               0.0s
 => [1/5] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a       0.0s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a       0.0s
 => [internal] load build context                                                                                               0.0s
 => => transferring context: 123B                                                                                               0.0s
 => CACHED [2/5] WORKDIR /app                                                                                                   0.0s
 => CACHED [3/5] COPY requirements.txt .                                                                                        0.0s
 => CACHED [4/5] RUN pip install -r requirements.txt                                                                            0.0s
 => CACHED [5/5] COPY . .                                                                                                       0.0s
 => exporting to image                                                                                                          0.1s
 => => exporting layers                                                                                                         0.0s
 => => exporting manifest sha256:0c34f2d4bf3349f8f7339cbb13882bc7169298e19b037cb4cbac6caf0d0e7f3a                               0.0s
 => => exporting config sha256:d05c195518c4e2950e2e41db853cdc791a9f45872f3d44d85ac4dc85992b357f                                 0.0s
 => => exporting attestation manifest sha256:eaff2efdd351e6af9b8fae1ee43305e09f2e03885995dc24c6fa72ab19bec3ec                   0.0s
 => => exporting manifest list sha256:a493e4006b4e1ace167d330f10d0bb349160f7ca0a903654230c60cb8053a05e                          0.0s
 => => naming to docker.io/library/my-app:4.0                                                                                   0.0s
 => => unpacking to docker.io/library/my-app:4.0                                                                                0.0s

```

## .dockerignore

Файл `.dockerignore` исключает ненужные файлы из контекста сборки.
Это уменьшает размер образа и предотвращает случайный сброс кэша.

```
venv/
__pycache__/
.git
Dockerfile
node_modules/
.idea/
*.pyc
```

## Multi-stage builds

### Проблема

Болльшой вес итогового образа конейнера после сборки

#### Dockerfile без myltistage

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

```bash
docker build -t react-nginx:1.0 .
```

```
[+] Building 53.7s (11/11) FINISHED                                                                                                                                    docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.0s
 => => transferring dockerfile: 131B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/node:18                                                                                  0.8s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 67B                                                                                                            0.0s
 => [1/6] FROM docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                            0.0s
 => => resolve docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                            0.0s
 => [internal] load build context                                                                                                           0.1s
 => => transferring context: 844B                                                                                                           0.1s
 => CACHED [2/6] WORKDIR /app                                                                                                               0.0s
 => [3/6] COPY package*.json .                                                                                                              0.0s
 => [4/6] RUN npm install                                                                                                                   22.9s
 => [5/6] COPY . .                                                                                                                          0.5s
 => [6/6] RUN npm run build                                                                                                                 5.3s
 => exporting to image                                                                                                                      23.8s
 => => exporting layers                                                                                                                     10.3s
 => => exporting manifest sha256:c06b37f2e2186fd3e4d069e178a66abc106f1cb6bf54e7f92654b1de0475bd30                                           0.0s
 => => exporting config sha256:cd0c29f1bed7e59528ed2b4a2b1e634e90d55ced3444126a3566b7d44c3cc3b7                                             0.0s
 => => exporting attestation manifest sha256:bcd7428fad01ff2670a4121f71f8bff914fb80ad57bcb1f67b2d887802e57cfb                               0.0s
 => => exporting manifest list sha256:f41e6446c06e3dc16cdf5c1a6a97f03e4fd715b5fc6af5976522d14397a33fe0                                      0.0s
 => => naming to docker.io/library/react-nginx:1.0                                                                                          0.0s
 => => unpacking to docker.io/library/react-nginx:1.                                                                                        13.4s
```

```bash
docker images
```

```
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
react-nginx:1.0   f41e6446c06e       2.12GB          492MB
```

### Решение

Использование multistage для избавления от лишних зависимостей

#### Dockerfile c myltistage

```dockerfile
#Этап 1 - сборка

FROM node:18 AS build
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

#Этап 2 - запуск
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
```

```bash
docker build -t react-nginx:1.0 .
```

```
[+] Building 31.2s (14/14) FINISHED                                                                                                                                    docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.0s
 => => transferring dockerfile: 273B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/nginx:alpine                                                                             0.8s
 => [internal] load metadata for docker.io/library/node:18                                                                                  0.8s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 67B                                                                                                            0.0s
 => [build 1/6] FROM docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                      0.0s
 => => resolve docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                            0.0s
 => [internal] load build context                                                                                                           0.1s
 => => transferring context: 986B                                                                                                           0.1s
 => CACHED [stage-1 1/2] FROM docker.io/library/nginx:alpine@sha256:54f2a904c251d5a34adf545a72d32515a15e08418dae0266e23be2e18c66fefa        0.0s
 => => resolve docker.io/library/nginx:alpine@sha256:54f2a904c251d5a34adf545a72d32515a15e08418dae0266e23be2e18c66fefa                       0.0s
 => CACHED [build 2/6] WORKDIR /app                                                                                                         0.0s
 => [build 3/6] COPY package*.json .                                                                                                        0.0s
 => [build 4/6] RUN npm install                                                                                                             20.8s
 => [build 5/6] COPY . .                                                                                                                    0.5s
 => [build 6/6] RUN npm run build                                                                                                           7.5s
 => [stage-1 2/2] COPY --from=build /app/build /usr/share/nginx/html                                                                        0.0s
 => exporting to image                                                                                                                      0.3s
 => => exporting layers                                                                                                                     0.1s
 => => exporting manifest sha256:772bf97ad772352c043668c60c25629a9b6a394760d8f11c1504fe2ef1060576                                           0.0s
 => => exporting config sha256:2d83346cdcecabedb1d3a2539958227620aa18e79f80938736675093d864f747                                             0.0s
 => => exporting attestation manifest sha256:482de8b09da981dcd13ff805b82906e1bb6e623c117ca4880b930bb45e884047                               0.0s
 => => exporting manifest list sha256:ce52f54ce6f9ed40ae1be963c51b8fc88518a8b91f0b22140f084797cc0fcf5d                                      0.0s
 => => naming to docker.io/library/react-nginx:1.0                                                                                          0.0s
 => => unpacking to docker.io/library/react-nginx:1.0                                                                                       0.0s
```

```bash
docker images
```

```
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
react-nginx:1.0   ce52f54ce6f9         94MB         26.3MB
```

## ARG vs ENV
| | ARG | ENV |
|--|-----|-----|
| Когда доступна | Только во время `docker build` | Во время работы контейнера |
| Где использовать | `FROM node:${VERSION}` | `DATABASE_URL`, `PORT` |
| Остаётся в образе | Нет | Да |

```dockerfile
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}

ENV PORT=5000
ENV DATABASE_URL=postgresql://localhost:5432/mydb
```

```bash
docker build -t app:1.0 -f Dockerfile.ENV_ARG .
```

```
[+] Building 1.3s (5/5) FINISHED                                                                                                            docker:default
 => [internal] load build definition from Dockerfile.ENV_ARG                                                                                0.0s
 => => transferring dockerfile: 159B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/node:18                                                                                  1.0s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => CACHED [1/1] FROM docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                     0.0s
 => => resolve docker.io/library/node:18@sha256:c6ae79e38498325db67193d391e6ec1d224d96c693a8a4d943498556716d3783                            0.0s
 => exporting to image                                                                                                                      0.1s
 => => exporting layers                                                                                                                     0.0s
 => => exporting manifest sha256:83fcb4600f7635c767574c4ac0d73ecf813f833a3f90d3e79913a55b209eeb2a                                           0.0s
 => => exporting config sha256:ec17c556d4fae54db80aaa7f4a8f66e3715c2043b5f9c75c6c336c9956c00bd4                                             0.0s
 => => exporting attestation manifest sha256:9db2c529a66211fb40d2e5f21a4d4a638f4b6d2c78d192671e5a4e291920094f                               0.0s
 => => exporting manifest list sha256:9c15936c661ab85bf6b28e88319512d784280b46cfd81d44a71368ef2fb438ae                                      0.0s
 => => naming to docker.io/library/app:1.0                                                                                                  0.0s
 => => unpacking to docker.io/library/app:1.0                                                                                               0.0s
```

## Безопасность (non-root пользователь)

Контейнер по умолчанию запускается от root — это опасно.
Создаём отдельного пользователя:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

USER appuser

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

```bash
docker build -t app:2.0 -f Dockerfile.NonRoot .
```

```
[+] Building 164.5s (9/9) FINISHED                                                                                                          docker:default
 => [internal] load build definition from Dockerfile.NonRoot                                                                                0.0s
 => => transferring dockerfile: 258B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                         0.9s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.8s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.8s
 => [internal] load build context                                                                                                           134.8s
 => => transferring context: 242.81MB                                                                                                       134.7s
 => CACHED [2/4] WORKDIR /app                                                                                                               0.0s
 => [3/4] COPY . .                                                                                                                          9.3s
 => [4/4] RUN groupadd -r appgroup && useradd -r -g appgroup appuser                                                                        0.8s
 => exporting to image                                                                                                                      17.7s
 => => exporting layers                                                                                                                     6.2s
 => => exporting manifest sha256:b7d5571c609d14f22e91d25f614c6225b71c8e81996ae7966577f52c6542aba4                                           0.0s
 => => exporting config sha256:c7a769e733fbb97cf3cd95bc74f4431082ea3ed37eea1d5298d4c8fd888a8bd9                                             0.0s
 => => exporting attestation manifest sha256:bed3308b69c745a597378cdfec4dae9e2bbb71b66117b87799d229de83ecda89                               0.0s
 => => exporting manifest list sha256:1663aaa4f470654a2e9ce4734f21ccc9a64d204f63d24b272da40d2aa335954d                                      0.0s
 => => naming to docker.io/library/app:2.0                                                                                                  0.0s
 => => unpacking to docker.io/library/app:2.0                                              11.4s                                            0.0s
```

```bash
docker run --rm app:2.0 whoami
```

```
appuser
```

## HEALTHCHECK

HEALTHCHECK позволяет Docker проверять что приложение работает корректно.
Без него Docker знает только что процесс запущен, но не отвечает ли приложение.

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

```bash
docker build -t app:3.0 -f Dockerfile.Healthcheck .
```

```
[+] Building 323.3s (12/12) FINISHED                                                                                                        docker:default
 => [internal] load build definition from Dockerfile.Healthcheck                                                                            0.0s
 => => transferring dockerfile: 509B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                         0.8s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 107B                                                                                                           0.0s
 => CACHED [1/7] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a            0.0s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                   0.0s
 => [internal] load build context                                                                                                           277.5s
 => => transferring context: 3.77MB                                                                                                         277.4s
 => [2/7] RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*                                                      5.8s
 => [3/7] WORKDIR /app                                                                                                                      0.0s
 => [4/7] COPY requirements.txt .                                                                                                           0.0s
 => [5/7] RUN pip install -r requirements.txt                                                                                               8.6s
 => [6/7] COPY . .                                                                                                                          16.1s
 => [7/7] RUN groupadd -r appgroup && useradd -r -g appgroup appuser                                                                        0.7s
 => exporting to image                                                                                                                      19.3s
 => => exporting layers                                                                                                                     6.5s
 => => exporting manifest sha256:0efa4e3f5d32d95660e3d05c78778f308ff99e036b438bf13d639fc6b0d24872                                           0.0s
 => => exporting config sha256:f532ecd54b148704e208c5cb00f6ee884026b2cbe3d2d6451d3bf7584155cad4                                             0.0s
 => => exporting attestation manifest sha256:b280d2257392801b42e3773a65c1779597042ba8c60e87729ca78a1c8b52a538                               0.0s
 => => exporting manifest list sha256:581c466e51a9e288f3adf7392c128d5e70a869609339225a865f7336b391782c                                      0.0s
 => => naming to docker.io/library/app:3.0                                                                                                  0.0s
 => => unpacking to docker.io/library/app:3.0                                                                                              12.6s
```

```bash
docker run -d -p 5000:5000 app:3.0
```

```
0a43935d66a8fc95388a348e5d8e254dece8442901f21b51f471d6b9fd977d59
```

Ждем 30 секунд

```bash
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS                    PORTS                                         NAMES
8fac608abb35   app:3.0   "uvicorn app:app --h…"   32 seconds ago   Up 31 seconds (healthy)   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   infallible_antonelli
```

## Multi-stage Java

Практика в multistage. Критерии:  Итоговый образ содержит runtime, а не sdk. 

```dockerfile
# Этап 1 — сборка (тяжёлый JDK)
FROM eclipse-temurin:17 AS builder
WORKDIR /app
COPY Main.java .
RUN javac Main.java

# Этап 2 — запуск (лёгкий JRE)
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/Main.class .
CMD ["java", "Main"]
```

```bash
docker build -t java-app:1.0 .
```

```
[+] Building 29.4s (13/13) FINISHED                                                                                                         docker:default
 => [internal] load build definition from Dockerfile                                                                                        0.0s
 => => transferring dockerfile: 301B                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/eclipse-temurin:17-jre-alpine                                                            1.8s
 => [internal] load metadata for docker.io/library/eclipse-temurin:17                                                                       1.8s
 => [internal] load .dockerignore                                                                                                           0.0s
 => => transferring context: 2B                                                                                                             0.0s
 => [builder 1/4] FROM docker.io/library/eclipse-temurin:17@sha256:91b6210cce02091f6f0798a83ec51aa223828242c5a21a85793bb8c28dc891c4         25.9s
 => => resolve docker.io/library/eclipse-temurin:17@sha256:91b6210cce02091f6f0798a83ec51aa223828242c5a21a85793bb8c28dc891c4                 0.0s
 => => sha256:66812886718425a70cc833106c2e62986c69cda7aaf5e097e9ccb29e35fcdd78 2.28kB / 2.28kB                                              0.4s
 => => sha256:cbe16ec1ccf716ef4daa5cbbc11cf7e56b21761f932235a5580f818bd9a6c874 158B / 158B                                                  0.4s
 => => sha256:2caaed84de85b23a93e1a09dcd67163c88a3f56bb56584ee1882cd855b65c14c 145.91MB / 145.91MB                                          23.8s
 => => sha256:83759bf057249226499f0acdd8b1c78ff24427d05c3110d93876ed1103004dfe 24.04MB / 24.04MB                                            9.2s
 => => sha256:d1f56e4c7f2f2a1415c59803638274d488a73b61a8e1f9cbd9cb280327e8d21e 388B / 388B                                                  0.2s
 => => sha256:81e2f2053c8fa702b6863110b55c09e67f6adeb78b4672745958c4d8b3d056c5 41.56MB / 41.56MB                                            8.8s
 => => extracting sha256:81e2f2053c8fa702b6863110b55c09e67f6adeb78b4672745958c4d8b3d056c5                                                   2.6s
 => => extracting sha256:d1f56e4c7f2f2a1415c59803638274d488a73b61a8e1f9cbd9cb280327e8d21e                                                   0.0s
 => => extracting sha256:83759bf057249226499f0acdd8b1c78ff24427d05c3110d93876ed1103004dfe                                                   1.1s
 => => extracting sha256:2caaed84de85b23a93e1a09dcd67163c88a3f56bb56584ee1882cd855b65c14c                                                   1.3s
 => => extracting sha256:cbe16ec1ccf716ef4daa5cbbc11cf7e56b21761f932235a5580f818bd9a6c874                                                   0.0s
 => => extracting sha256:66812886718425a70cc833106c2e62986c69cda7aaf5e097e9ccb29e35fcdd78                                                   0.0s
 => [internal] load build context                                                                                                           0.1s
 => => transferring context: 160B                                                                                                           0.0s
 => [stage-1 1/3]                                                                                                                                      FROM docker.io/library/eclipse-temurin:17-jre-alpine@sha256:02320dd4ce20e243dfb915c686089cf9315c763084fafbb12d5c9993aee18b57               13.6s
 => => resolve docker.io/library/eclipse-temurin:17-jre-alpine@sha256:02320dd4ce20e243dfb915c686089cf9315c763084fafbb12d5c9993aee18b57      0.0s
 => => sha256:bb5bb06f25c55e382a04c0a0ba3681a1f392b0894814fcd6dfc7ec27615aad47 2.28kB / 2.28kB                                              0.2s
 => => sha256:4f9b826e558088052ee5d0b1ffe535bfebc159275ee5601967839346cebfe243 128B / 128B                                                  0.2s
 => => sha256:1e2a2f574cbcb3f5f0d1d81c43cd8f7ed0ae3a658e4fa49f240978906d68f1f9 47.23MB / 47.23MB                                            14.8s
 => => sha256:33155d10cbc71fdb14f9df0a7aab9f4991457ef842a4b3faba9384696971d92b 16.82MB / 16.82MB                                            5.8s
 => => extracting sha256:33155d10cbc71fdb14f9df0a7aab9f4991457ef842a4b3faba9384696971d92b                                                   0.7s
 => => extracting sha256:1e2a2f574cbcb3f5f0d1d81c43cd8f7ed0ae3a658e4fa49f240978906d68f1f9                                                   0.0s
 => => extracting sha256:4f9b826e558088052ee5d0b1ffe535bfebc159275ee5601967839346cebfe243                                                   0.0s
 => => extracting sha256:bb5bb06f25c55e382a04c0a0ba3681a1f392b0894814fcd6dfc7ec27615aad47                                                   0.0s
 => [stage-1 2/3] WORKDIR /app                                                                                                              0.2s
 => [builder 2/4] WORKDIR /app                                                                                                              0.4s
 => [builder 3/4] COPY Main.java .                                                                                                          0.0s
 => [builder 4/4] RUN javac Main.java                                                                                                       0.8s
 => [stage-1 3/3] COPY --from=builder /app/Main.class .                                                                                     0.0s
 => exporting to image                                                                                                                      0.2s
 => => exporting layers                                                                                                                     0.1s
 => => exporting manifest sha256:a7bf0b9157a5c41ce4430d6c01d371e2c6b9743a859d27463d6e049bb2b57107                                           0.0s
 => => exporting config sha256:ffe0caf4a1adea298c88cf20788bf665770093ccdcaabd0b8670194dbf5c42ae                                             0.0s
 => => exporting attestation manifest sha256:9ab47e3918f6a595e39ee498cac0ae00cb37354a1a1d4e1aadb900200b8ff204                               0.0s
 => => exporting manifest list sha256:28b072fad27cd8e0e80c5133a4b74ef5e7e5d5f04dc6e703bc2694cf13858763                                      0.0s
 => => naming to docker.io/library/java-app:1.0                                                                                             0.0s
 => => unpacking to docker.io/library/java-app:1.0    
```

```bash
docker images
```

```
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
java-app:1.0      28b072fad27c        256MB         67.9MB
```

```bash
docker run --rm -it java-app:1.0 sh

/app # javac -version
sh: javac: not found
```

Итоговый образ содержит только JRE + скомпилированный класс, без JDK.
