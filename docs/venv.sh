#! /bin/bash

## install package:
apt install python3-virtualenv

## init venv on project root folder:
virtualenv venv

# load venv:
source venv/bin/activate

# view default package installed
pip freeze

# exit from venv:
deactivate
#source deactivate

# install from requirements.txt
pip3 install -r requirements.txt
