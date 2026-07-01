# Module 10 - Ansible Playbooks

## Что такое Playbook

Ad-Hoc команды (модуль 9) подходят для разовых проверок и быстрых действий, но не описывают весь сценарий настройки сервера и не сохраняются как код.

Playbook -  YAML который описываеющий желаемое состояние сервера целиком: список задач, которые выполняются по порядку. Playbook можно безопасно запускать многократно, на разных хостах, и результат будет предсказуемым.

## nginx-playbook.yml - структура

```yaml
---
- hosts: local
  become: true

  vars:
    nginx_port: 80

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install Nginx
      apt:
        name: nginx
        state: present

    - name: Start Nginx
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Configure Nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx

  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

## Запуск Playbook

```bash
ansible-playbook -i inventory.ini nginx-playbook.yml
```

Первый запуск - устанавливает nginx и создаёт конфиг:

```
TASK [Update apt cache] ********************
ok: [localhost]
TASK [Install Nginx] ***********************
ok: [localhost]
TASK [Start Nginx] *************************
ok: [localhost]
TASK [Configure Nginx] *********************
changed: [localhost]
RUNNING HANDLER [Restart Nginx] ************
changed: [localhost]

PLAY RECAP
localhost : ok=6 changed=2 unreachable=0 failed=0
```

Повторный запуск без изменений - идемпотентность в действии:

```
TASK [Configure Nginx] *********************
ok: [localhost]

PLAY RECAP
localhost : ok=5 changed=0 unreachable=0 failed=0
```

Handler `Restart Nginx` на этот раз не вызывается вообще - конфиг не изменился, перезапускать сервис незачем.

## Переменные (vars)

```yaml
vars:
  nginx_port: 80
```

Переменная задаётся один раз и переиспользуется в шаблоне (`nginx.conf.j2`) через синтаксис Jinja2 `{{ nginx_port }}`. Меняя значение переменной, можно разворачивать один и тот же playbook с разными настройками на разных хостах без правки самого шаблона.

## Шаблоны (template + Jinja2)

`nginx.conf.j2`:

```nginx
events {}

http {
    server {
        listen {{ nginx_port }};

        location / {
            return 200 'Hello from Ansible managed Nginx!';
        }
    }
}
```

Модуль `template` копирует файл на сервер, предварительно отрендерив его через Jinja2 - `{{ nginx_port }}` заменяется реальным значением переменной (`80`), и на сервер уезжает уже готовый конфиг без фигурных скобок.

## Handlers

Handler - это таск, который выполняется не сам по себе, а только при `notify` от другого таска, и только если этот таск вернул `changed: true`.

```yaml
tasks:
  - name: Configure Nginx
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: Restart Nginx

handlers:
  - name: Restart Nginx
    service:
      name: nginx
      state: restarted
```

Это предотвращает лишние перезапуски сервиса - nginx перезапускается только когда конфиг реально поменялся, а не при каждом запуске playbook.

## Roles - эссе

Теория про переиспользование кода через Ansible Roles - в `essay-roles.md`.

Кратко: монолитный playbook плохо масштабируется на множество проектов - баг приходится чинить в каждой копии вручную. Roles разбивают логику на стандартизированную структуру директорий (`tasks/`, `handlers/`, `templates/`, `vars/`), и тогда главный playbook превращается в короткий список подключаемых ролей:

```yaml
- hosts: webservers
  roles:
    - nginx
    - postgres
```