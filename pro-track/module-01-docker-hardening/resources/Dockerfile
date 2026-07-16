FROM python:3.8-slim-buster

WORKDIR /app

RUN sed -i 's/deb.debian.org/archive.debian.org/g; s|security.debian.org|archive.debian.org/debian-security|g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends curl=7.64.0-4+deb10u9 && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]