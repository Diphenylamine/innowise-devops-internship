# Module 09 - Ansible

## Что такое Ansible

Ansible — инструмент управления конфигурациями (Configuration Management).

Три ключевых свойства:
- Декларативный — описываешь что хочешь получить, а не как это сделать
- Agentless — работает по SSH, ничего не нужно устанавливать на сервер
- Идемпотентный — повторный запуск не ломает систему, приводит к тому же результату

## Установка

```bash
pip install ansible --break-system-packages
export PATH=$PATH:/home/diphenylamine/.local/bin
echo 'export PATH=$PATH:/home/diphenylamine/.local/bin' >> ~/.bashrc
```

```bash
ansible --version
```

```
ansible [core 2.21.1]
 executable location = /home/diphenylamine/.local/bin/ansible
 python version = 3.12.3
```

## inventory.ini

Inventory — файл со списком серверов которыми управляет Ansible.

```ini
[local]
localhost ansible_connection=local
```

`ansible_connection=local` — подключаться локально, без SSH.

Inventory используется для указания Ansible какими серверами управлять. В нём серверы группируются — например [webservers], [dbservers], [local]. При запуске команды указываешь группу и Ansible применяет действие ко всем серверам в ней.
В данном случае [local] — группа с одним сервером localhost для локального тестирования.

## Ad-Hoc команды

Ad-Hoc команды — это разовые команды Ansible без написания playbook.
Синтаксис: `ansible [группа] -i [inventory] -m [модуль] -a "[аргументы]"`

### ping

Проверка связи с хостами:

```bash
ansible local -i inventory.ini -m ping
```

```
localhost | SUCCESS => {
   "changed": false,
   "ping": "pong"
}
```

### setup

Сбор фактов о системе — возвращает огромный JSON с информацией об ОС,
IP адресах, железе и т.д.:

```bash
ansible local -i inventory.ini -m setup
```

### apt — установка пакета

```bash
ansible local -i inventory.ini -m apt -a "name=nginx state=present" --become
```

```
localhost | CHANGED => {
   "changed": true,
   ...
}
```

### Идемпотентность

Повторный запуск той же команды:

```bash
ansible local -i inventory.ini -m apt -a "name=nginx state=present" --become
```

```
localhost | SUCCESS => {
   "changed": false
}
```

Ansible увидел что nginx уже установлен — ничего не делал.

### service — управление сервисом

```bash
ansible local -i inventory.ini -m service -a "name=nginx state=started enabled=yes" --become
```

```
localhost | SUCCESS => {
   "changed": false,
   "state": "started"
}
```

### file — создание директории

```bash
ansible local -i inventory.ini -m file -a "path=/tmp/test-ansible state=directory"
```

```
localhost | CHANGED => {
   "changed": true,
   "state": "directory"
}
```

### copy — копирование файла

```bash
ansible local -i inventory.ini -m copy -a "src=inventory.ini dest=/tmp/test-ansible/inventory.bak"
```

```
localhost | CHANGED => {
   "changed": true,
   "dest": "/tmp/test-ansible/inventory.bak"
}
```