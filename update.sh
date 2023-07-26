#!/bin/bash
sudo git config --global --add safe.directory .
sudo git pull
sudo service apache2 restart
