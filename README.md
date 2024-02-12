# Мануал
## Подготвка сервера
### Обновление репозитория и upgrade пакетов до текущих версий
```sh
apt update && apt dist-upgrade -y
```

### Задаём имя сервера
```sh
hostnamectl set-hostname mednotesrv && reboot
```

### Установка необходимых для работы пакетов
```sh
apt install -y git build-essential libssl-dev libffi-dev sshpass python3-virtualenv python3-dev dos2unix screen libpq-dev
```
```sh
apt install -y postgresql postgresql-contrib
```

### Выставляем правильный часовой пояс
```sh
timedatectl set-timezone Europe/Moscow
```

### Добавляем русскую локаль
```sh
locale-gen "ru_RU.UTF-8"
```
```sh
localectl set-locale LANG=ru_RU.UTF-8
```
