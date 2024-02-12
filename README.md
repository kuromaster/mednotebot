# Мануал
## Подготовка сервера
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

### Установка БД PostgeSQL
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

### Настройка firewall
#### разрешаем все исходящие соединения
```sh
ufw default allow outgoing
```
#### разрешаем доступ к ssh для вашего внешнего ip
```sh
ufw allow from ВАШ_ВНЕШНИЙ_IP to any port 22
```
#### если есть локальная сеть, то и для неё можно открыть доступ к ssh
```sh
ufw allow from 192.168.201.0/24 to any port 22
```
#### включаем ufw
```sh
ufw enable
```
#### проверяем настрйоки
```sh
ufw status
```


```sh
```
