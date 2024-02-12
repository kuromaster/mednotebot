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

## установка бота
### скачиваем из гита нашего бота
```sh
git clone -b master https://github.com/kuromaster/mednotebot.git /opt/mednotebot
```

### создаём виртуальное окружение и активируем его
```sh
cd /opt/mednotebot && virtualenv venv && source /opt/mednotebot/venv/bin/activate
```

### устанавливаем пакеты из файла requirements.txt
```sh
pip3 install -r requirements.txt
```

### создаём недостающие каталоги
```sh
mkdir -p {cred,config}
```

### правим .env по пути /opt/mednotebot/config
```conf
BOT_TOKEN = XXXXX:XXXXXXXXX
APP_NAME = medtest

PG_USER = dbuser
PG_PWD = XXXXX
PG_HOST = 127.0.0.1
PG_DBNAME = mednote

MAEZZTRO_TID = XXXXX
```
