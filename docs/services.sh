# 0. Check exute file first string:
(venv) root@dcsrv03:/opt/mednotebot# which python3
/opt/mednotebot/venv/bin/python3

vim /opt/mednotebot/main.py
#! /opt/mednotebot/venv/bin/python3

# 1. link to /usr/bin
ln -s /opt/mednotebot/main.py /usr/bin/mednotebot

# 2. Create service
vim /etc/systemd/system/mednotebot.service

[Unit]
Description=MedNoteBot
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/mednotebot
Restart=on-abort
WorkingDirectory=/opt/mednotebot

[Install]
WantedBy=multi-user.target

# 3. Service
systemctl daemon-reload
systemctl restart mednotebot
systemctl status mednotebot.service
systemctl enable mednotebot.service
