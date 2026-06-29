# Module 01 — Docker Basics

## Установка
```bash
docker --version
```
```
Docker version 29.2.1, build a5c7197
```

```bash
docker info
```
```
Client:
 Version:    29.2.1
 Context:    desktop-linux
 Debug Mode: false
 Plugins:
  agent: create or run AI agents (Docker Inc.)
    Version:  v1.29.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-agent.exe
  ai: Docker AI Agent - Ask Gordon (Docker Inc.)
    Version:  v1.19.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-ai.exe
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.32.1-desktop.1
    Path:     C:\Program Files\Docker\cli-plugins\docker-buildx.exe
  compose: Docker Compose (Docker Inc.)
    Version:  v5.1.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-compose.exe
  debug: Get a shell into any image or container (Docker Inc.)
    Version:  0.0.47
    Path:     C:\Program Files\Docker\cli-plugins\docker-debug.exe
  desktop: Docker Desktop commands (Docker Inc.)
    Version:  v0.3.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-desktop.exe
  dhi: CLI for managing Docker Hardened Images (Docker Inc.)
    Version:  v0.0.1
    Path:     C:\Users\Diphenylamine\.docker\cli-plugins\docker-dhi.exe
  extension: Manages Docker extensions (Docker Inc.)
    Version:  v0.2.31
    Path:     C:\Program Files\Docker\cli-plugins\docker-extension.exe
  init: Creates Docker-related starter files for your project (Docker Inc.)
    Version:  v1.4.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-init.exe
  mcp: Docker MCP Plugin (Docker Inc.)
    Version:  v0.40.1
    Path:     C:\Program Files\Docker\cli-plugins\docker-mcp.exe
  model: Docker Model Runner (Docker Inc.)
    Version:  v1.1.5
    Path:     C:\Program Files\Docker\cli-plugins\docker-model.exe
  offload: Docker Offload (Docker Inc.)
    Version:  v0.5.70
    Path:     C:\Program Files\Docker\cli-plugins\docker-offload.exe
  pass: Docker Pass Secrets Manager Plugin (beta) (Docker Inc.)
    Version:  v0.0.24
    Path:     C:\Program Files\Docker\cli-plugins\docker-pass.exe
  sandbox: Docker Sandbox (Docker Inc.)
    Version:  v0.12.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-sandbox.exe
  sbom: View the packaged-based Software Bill Of Materials (SBOM) for an image (Anchore Inc.)
    Version:  0.6.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-sbom.exe
  scout: Docker Scout (Docker Inc.)
    Version:  v1.20.1
    Path:     C:\Program Files\Docker\cli-plugins\docker-scout.exe

Server:
 Containers: 3
  Running: 0
  Paused: 0
  Stopped: 3
 Images: 3
 Server Version: 29.2.1
 Storage Driver: overlayfs
  driver-type: io.containerd.snapshotter.v1
 Logging Driver: json-file
 Cgroup Driver: cgroupfs
 Cgroup Version: 2
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local splunk syslog
 CDI spec directories:
  /etc/cdi
  /var/run/cdi
 Discovered Devices:
  cdi: docker.com/gpu=webgpu
 Swarm: inactive
 Runtimes: io.containerd.runc.v2 nvidia runc
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: dea7da592f5d1d2b7755e3a161be07f43fad8f75
 runc version: v1.3.4-0-gd6d73eb8
 init version: de40ad0
 Security Options:
  seccomp
   Profile: builtin
  cgroupns
 Kernel Version: 6.6.87.2-microsoft-standard-WSL2
 Operating System: Docker Desktop
 OSType: linux
 Architecture: x86_64
 CPUs: 12
 Total Memory: 13.58GiB
 Name: docker-desktop
 ID: f98af559-1398-4e32-9acc-506a94aa1d84
 Docker Root Dir: /var/lib/docker
 Debug Mode: false
 HTTP Proxy: http.docker.internal:3128
 HTTPS Proxy: http.docker.internal:3128
 No Proxy: hubproxy.docker.internal
 Labels:
  com.docker.desktop.address=npipe://\\.\pipe\docker_cli
 Experimental: false
 Insecure Registries:
  hubproxy.docker.internal:5555
  127.0.0.0/8
  ::1/128
 Live Restore Enabled: false
 Firewall Backend: iptables
```

## Hello World
```bash
docker run hello-world
```
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
4f55086f7dd0: Pull complete
d5e71e642bf5: Download complete
Digest: sha256:96498ffd522e70807ab6384a5c0485a79b9c7c08ca79ba08623edcad1054e62d
Status: Downloaded newer image for hello-world:latest
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.
...
To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash
...
Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/
...
For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

## Интерактивный режим
```bash
docker run -it ubuntu bash
whoami
cat /etc/os-release
exit
```
```
Unnable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
d1f56e4c7f2f: Pull complete
81e2f2053c8f: Pull complete
107e4f1717f2: Download complete
Digest: sha256:53958ec7b67c2c9355df922dd08dbf0360611f8c3cdb656875e81873db9ffdba
Status: Downloaded newer image for ubuntu:latest
...
root@9997c0f354ac:/# whoami
root
...
root@9997c0f354ac:/# cat /etc/os-release
PRETTY_NAME="Ubuntu 26.04 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
VERSION="26.04 LTS (Resolute Raccoon)"
VERSION_CODENAME=resolute
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=resolute
LOGO=ubuntu-logo
...
root@9997c0f354ac:/# uname -r
6.6.87.2-microsoft-standard-WSL2
...
root@9997c0f354ac:/# exit
```

## Фоноый режим
```bash
docker run -d nginx
```
```
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
d1f56e4c7f2f: Pull complete
81e2f2053c8f: Pull complete
107e4f1717f2: Download complete
Digest: sha256:53958ec7b67c2c9355df922dd08dbf0360611f8c3cdb656875e81873db9ffdba
Status: Downloaded newer image for ubuntu:latest
root@9997c0f354ac:/# whoami
root
root@9997c0f354ac:/# cat /etc/os-release
PRETTY_NAME="Ubuntu 26.04 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
VERSION="26.04 LTS (Resolute Raccoon)"
VERSION_CODENAME=resolute
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=resolute
LOGO=ubuntu-logo
root@9997c0f354ac:/# uname -r
6.6.87.2-microsoft-standard-WSL2
root@9997c0f354ac:/# exit\356\201\226\356\200\273\356\203\201\356\203\273\356\203\271\356\204\235
PS D:\internship\innowise-devops-internship> docker run -d nginx
Unable to find image 'nginx:latest' locally
latest: Pulling from library/nginx
1645c1e06f46: Pull complete
cd9307c9ecd8: Pull complete
df68ee7e7a00: Pull complete
acf093e7a04f: Pull complete
1b30016634d5: Pull complete
e95a6c7ea7d4: Pull complete
fcb6fd84b2a0: Pull complete
1cf7d051b485: Download complete
e2c07e54e55a: Download complete
Digest: sha256:ec4ed8b5299e5e90694af7750eb6dffd2627317d30544d056b0371f8082f7bce
Status: Downloaded newer image for nginx:latest
17cc5910106849168f6e3b4b49d46c4d0a9528f92f303adc0a925ac66b659c80
```

## Управление

```bash
docker ps
docker ps -a
```
```
PS D:\internship\innowise-devops-internship> docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS     NAMES
17cc59101068   nginx     "/docker-entrypoint.…"   3 minutes ago   Up 3 minutes   80/tcp    romantic_hellman
9997c0f354ac   ubuntu    "bash"                   9 minutes ago   Up 9 minutes             brave_satoshi
...
PS D:\internship\innowise-devops-internship> docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                      PORTS                    NAMES
17cc59101068   nginx         "/docker-entrypoint.…"   3 minutes ago    Up 3 minutes                80/tcp                   romantic_hellman
9997c0f354ac   ubuntu        "bash"                   9 minutes ago    Up 9 minutes                                         brave_satoshi
0cd91605216b   hello-world   "/hello"                 10 minutes ago   Exited (0) 10 minutes ago                            serene_kepler
c4b9a1be78ec   postgres      "docker-entrypoint.s…"   3 months ago     Exited (0) 3 weeks ago                               my-postgres
e8eb03b0f8d6   redis         "docker-entrypoint.s…"   3 months ago     Exited (255) 3 months ago   0.0.0.0:6379->6379/tcp   my-redis
```

## Проброс портов
```bash
docker stop 17cc59101068
docker run -d -p 8080:80 nginx
netstat -ano | findstr :8080
docker run -d -p 8088:80 nginx
```
```
PS D:\internship\innowise-devops-internship> docker stop 17cc59101068
17cc59101068
...
PS D:\internship\innowise-devops-internship> docker run -d -p 8080:80 nginx
dec90a871fa20cb24f5a439a40cc4d7e102ebd6484c542976595a3a671fec395
docker: Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:8080 -> 127.0.0.1:0: listen tcp 0.0.0.0:8080: bind: An attempt was made to access a socket in a way forbidden by its access permissions.
...
Run 'docker run --help' for more information
...
PS D:\internship\innowise-devops-internship> netstat -ano | findstr :8080
  TCP    0.0.0.0:8080           0.0.0.0:0              LISTENING       4
  TCP    [::]:8080              [::]:0                 LISTENING       4
  ...
PS D:\internship\innowise-devops-internship> docker run -d -p 8088:80 nginx
7fc59ef0c052cd62d9d6b28cbcd6f158279b7677a545e7a4d12e196b36bdd336
```
Порт 8080 занят системным процессом Windows (PID 4), использован порт 8088.
Открыт http://localhost:8088 — отображается страница "Welcome to nginx!"

## Логи
```bash
docker ps
docker logs 7fc59ef0c052
docker logs -f 7fc59ef0c052
```
```
PS D:\internship\innowise-devops-internship> docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                     NAMES
7fc59ef0c052   nginx     "/docker-entrypoint.…"   6 minutes ago    Up 6 minutes    0.0.0.0:8088->80/tcp, [::]:8088->80/tcp   loving_cannon
9997c0f354ac   ubuntu    "bash"                   24 minutes ago   Up 24 minutes                                             brave_satoshi
...
PS D:\internship\innowise-devops-internship> docker logs 7fc59ef0c052
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/06/25 02:39:29 [notice] 1#1: using the "epoll" event method
2026/06/25 02:39:29 [notice] 1#1: nginx/1.31.2
2026/06/25 02:39:29 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
2026/06/25 02:39:29 [notice] 1#1: OS: Linux 6.6.87.2-microsoft-standard-WSL2
2026/06/25 02:39:29 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2026/06/25 02:39:29 [notice] 1#1: start worker processes
2026/06/25 02:39:29 [notice] 1#1: start worker process 29
2026/06/25 02:39:29 [notice] 1#1: start worker process 30
2026/06/25 02:39:29 [notice] 1#1: start worker process 31
2026/06/25 02:39:29 [notice] 1#1: start worker process 32
2026/06/25 02:39:29 [notice] 1#1: start worker process 33
2026/06/25 02:39:29 [notice] 1#1: start worker process 34
2026/06/25 02:39:29 [notice] 1#1: start worker process 35
2026/06/25 02:39:29 [notice] 1#1: start worker process 36
2026/06/25 02:39:29 [notice] 1#1: start worker process 37
2026/06/25 02:39:29 [notice] 1#1: start worker process 38
2026/06/25 02:39:29 [notice] 1#1: start worker process 39
2026/06/25 02:39:29 [notice] 1#1: start worker process 40
172.17.0.1 - - [25/Jun/2026:02:40:30 +0000] "GET / HTTP/1.1" 200 896 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36" "-"
172.17.0.1 - - [25/Jun/2026:02:40:30 +0000] "GET /favicon.ico HTTP/1.1" 404 555 "http://localhost:8088/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36" "-"
2026/06/25 02:40:30 [error] 29#29: *1 open() "/usr/share/nginx/html/favicon.ico" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /favicon.ico HTTP/1.1", host: "localhost:8088", referrer: "http:
//localhost:8088/"
...
docker logs -f 7fc59ef0c052
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/06/25 02:39:29 [notice] 1#1: using the "epoll" event method
2026/06/25 02:39:29 [notice] 1#1: nginx/1.31.2
2026/06/25 02:39:29 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
2026/06/25 02:39:29 [notice] 1#1: OS: Linux 6.6.87.2-microsoft-standard-WSL2
2026/06/25 02:39:29 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2026/06/25 02:39:29 [notice] 1#1: start worker processes
2026/06/25 02:39:29 [notice] 1#1: start worker process 29
2026/06/25 02:39:29 [notice] 1#1: start worker process 30
2026/06/25 02:39:29 [notice] 1#1: start worker process 31
2026/06/25 02:39:29 [notice] 1#1: start worker process 32
2026/06/25 02:39:29 [notice] 1#1: start worker process 33
2026/06/25 02:39:29 [notice] 1#1: start worker process 34
2026/06/25 02:39:29 [notice] 1#1: start worker process 35
2026/06/25 02:39:29 [notice] 1#1: start worker process 36
2026/06/25 02:39:29 [notice] 1#1: start worker process 37
2026/06/25 02:39:29 [notice] 1#1: start worker process 38
2026/06/25 02:39:29 [notice] 1#1: start worker process 39
2026/06/25 02:39:29 [notice] 1#1: start worker process 40
172.17.0.1 - - [25/Jun/2026:02:40:30 +0000] "GET / HTTP/1.1" 200 896 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36" "-"
172.17.0.1 - - [25/Jun/2026:02:40:30 +0000] "GET /favicon.ico HTTP/1.1" 404 555 "http://localhost:8088/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36" "-"
2026/06/25 02:40:30 [error] 29#29: *1 open() "/usr/share/nginx/html/favicon.ico" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /favicon.ico HTTP/1.1", host: "localhost:8088", referrer: "http:
//localhost:8088/"
172.17.0.1 - - [25/Jun/2026:02:47:31 +0000] "GET / HTTP/1.1" 200 896 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0" "-"
172.17.0.1 - - [25/Jun/2026:02:47:31 +0000] "GET /favicon.ico HTTP/1.1" 404 153 "http://localhost:8088/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0" "-"
2026/06/25 02:47:31 [error] 31#31: *3 open() "/usr/share/nginx/html/favicon.ico" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /favicon.ico HTTP/1.1", host: "localhost:8088", referrer: "http:
//localhost:8088/"
172.17.0.1 - - [25/Jun/2026:02:47:44 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0" "-"
```

## Управление образами
```bash
docker images
docker rmi hello-world
docker images
```
```
PS D:\internship\innowise-devops-internship> docker images
                                                                                                                                                                                                                         i Info →   U  In Use
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   96498ffd522e       25.9kB         9.49kB    U 
nginx:latest         ec4ed8b5299e        241MB           66MB    U 
postgres:latest      a9abf4275f9e        649MB          168MB    U 
redis:latest         315270d16608        204MB         55.3MB    U 
ubuntu:latest        53958ec7b67c        160MB         45.3MB    U 
...
docker rmi hello-world
Untagged: hello-world:latest
Deleted: sha256:96498ffd522e70807ab6384a5c0485a79b9c7c08ca79ba08623edcad1054e62d
...
PS D:\internship\innowise-devops-internship> docker images
                                                                                                                                                                                                                         i Info →   U  In Use
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
nginx:latest      ec4ed8b5299e        241MB           66MB    U 
postgres:latest   a9abf4275f9e        649MB          168MB    U 
redis:latest      315270d16608        204MB         55.3MB    U 
ubuntu:latest     53958ec7b67c        160MB         45.3MB    U 
```

## Очистка
```bash
docker ps -a
docker stop 7fc59ef0c052 9997c0f354ac
docker rm 7fc59ef0c052 dec90a871fa2 17cc59101068 9997c0f354ac
docker ps -a
```
```
docker ps -a
CONTAINER ID   IMAGE      COMMAND                  CREATED          STATUS                      PORTS                                     NAMES
7fc59ef0c052   nginx      "/docker-entrypoint.…"   14 minutes ago   Up 14 minutes               0.0.0.0:8088->80/tcp, [::]:8088->80/tcp   loving_cannon
dec90a871fa2   nginx      "/docker-entrypoint.…"   15 minutes ago   Created                                                               frosty_leakey
17cc59101068   nginx      "/docker-entrypoint.…"   26 minutes ago   Exited (0) 16 minutes ago                                             romantic_hellman
9997c0f354ac   ubuntu     "bash"                   32 minutes ago   Up 32 minutes                                                         brave_satoshi
c4b9a1be78ec   postgres   "docker-entrypoint.s…"   3 months ago     Exited (0) 3 weeks ago                                                my-postgres
e8eb03b0f8d6   redis      "docker-entrypoint.s…"   3 months ago     Exited (255) 3 months ago   0.0.0.0:6379->6379/tcp                    my-redis
...
PS D:\internship\innowise-devops-internship> docker rm 7fc59ef0c052 dec90a871fa2 17cc59101068 9997c0f354ac
7fc59ef0c052
dec90a871fa2
17cc59101068
9997c0f354ac
...
PS D:\internship\innowise-devops-internship> docker ps -a
CONTAINER ID   IMAGE      COMMAND                  CREATED        STATUS                      PORTS                    NAMES
c4b9a1be78ec   postgres   "docker-entrypoint.s…"   3 months ago   Exited (0) 3 weeks ago                               my-postgres
e8eb03b0f8d6   redis      "docker-entrypoint.s…"   3 months ago   Exited (255) 3 months ago   0.0.0.0:6379->6379/tcp   my-redis
```
Контейнеры my-postgres и my-redis намеренно сохранены — это локальный проект, не связанный с модулем.