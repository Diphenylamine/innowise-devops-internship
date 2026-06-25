# Module 02 — Dockerfile

## Приложение
Простое REST API на FastAPI с одним эндпоинтом GET /, 
который возвращает JSON с приветственным сообщением.
...
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Привет! Твой бэкенд на FastAPI работает."}
```
...
```
fastapi
uvicorn
```

## Dockerfile

```dockerfile
FROM python:3.10-slim   # базовый образ Python

WORKDIR /app            # рабочая директория внутри контейнера

COPY . .                # копируем все файлы с хоста в /app

RUN pip install -r requirements.txt  # устанавливаем зависимости во время сборки

EXPOSE 5000             # документируем порт приложения

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]  # команда запуска
```

## Сборка образа
```bash
docker build -t my-app:1.0 .
```
```
[+] Building 22.1s (9/9) FINISHED                                                                                                                                                                                       docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                               0.1s
 => => transferring dockerfile: 211B                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.10-slim                                                                                3.7s
 => [internal] load .dockerignore                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                    0.0s
 => [1/4] FROM docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                          4.5s
 => => resolve docker.io/library/python:3.10-slim@sha256:a0c2acf33d1ad5355112e8ae578908f867a76f70f487b4632792d96889d78b7a                          0.0s
 => => sha256:45f9eb24ea676873533ee6f99f71066fd68d1719b427dca574341176c46c3fe9 254B / 254B                                                         0.4s
 => => sha256:e737dfad7625197cfb527045758452e364ec3da603df19d7781c8485d5d42f57 13.82MB / 13.82MB                                                   3.5s
 => => sha256:3b2876568ccf8422a3a4400c36c805333feb503711c9d44873a61295fb73ccfd 1.29MB / 1.29MB                                                     1.3s
 => => extracting sha256:3b2876568ccf8422a3a4400c36c805333feb503711c9d44873a61295fb73ccfd                                                          0.2s
 => => extracting sha256:e737dfad7625197cfb527045758452e364ec3da603df19d7781c8485d5d42f57                                                          0.9s
 => => extracting sha256:45f9eb24ea676873533ee6f99f71066fd68d1719b427dca574341176c46c3fe9                                                          0.0s
 => [internal] load build context                                                                                                                  0.0s
 => => transferring context: 430B                                                                                                                  0.0s
 => [2/4] WORKDIR /app                                                                                                                             0.1s
 => [3/4] COPY . .                                                                                                                                 0.0s
 => [4/4] RUN pip install -r requirements.txt                                                                                                      12.3s
 => exporting to image                                                                                                                             1.9s
 => => exporting layers                                                                                                                            1.1s
 => => exporting manifest sha256:5a443ef97d22f75d54f02fdb82c0a0876b9f1d954bb0a00b9b3ea7fc882eaaee                                                  0.0s
 => => exporting config sha256:ae0b5b1c11f3396db35555a41fdb271b73120fbca3a8a0717f2bed9aed668e86                                                    0.0s
 => => exporting attestation manifest sha256:cdfb8614f9bda46b639266c48aeb31abce6edee91de2fc174a75396d6b49f5f7                                      0.0s
 => => exporting manifest list sha256:4c8dc360b3ac287ac9feb7e4f84e023b9e6c5496dc3c3a5d04e88ef4dfba47e5                                             0.0s
 => => naming to docker.io/library/my-app:1.0                                                                                                      0.0s
 => => unpacking to docker.io/library/my-app:1.0                                                                                          
```

## Запуск
## Запуск

```bash
docker run -d -p 5000:5000 my-app:1.0
```

```
a1bd47146f99ce968bace4b0777c34f50363988898eefccfd4dc646bad79273e58b2c3d4e5f6...
```

Приложение доступно по http://localhost:5000

Ответ сервера:
```json
{"message": "Привет!"}
```