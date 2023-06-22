#!/bin/bash

#set -eu
# Color codes for echo statements
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to echo colored text
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

# Update package lists
sudo apt-get update

# Install necessary packages
sudo apt-get install apache2                # Apache HTTP Server
sudo apt-get install apache2-dev            # Apache development headers and module support
sudo apt-get install build-essential         # Essential build tools
sudo apt-get install python3-dev             # Python 3 development headers
sudo apt-get install libapache2-mod-wsgi-py3  # Apache module for hosting Python WSGI applications
sudo apt-get install libpq-dev              # PostgreSQL development headers
sudo apt-get install netcat                 # Networking utility for reading from/writing to network connections
sudo apt-get install default-libmysqlclient-dev   # MySQL development headers
sudo apt-get install  libmagic-dev             # Development files for libmagic, a file type detection library
sudo apt-get install expect

# Remove cached package lists
sudo rm -rf /var/lib/apt/lists/*

# Update package lists again
sudo apt-get update

#install snapd
sudo apt update
sudo apt install snapd
sudo snap install core; sudo snap refresh core

#install certbot, this is used for SSL certificate generation and management
sudo apt-get remove certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

print_green "INSTALLING MARIADB"
# Install MariaDB server
sudo apt-get install mariadb-server

# Start MariaDB service
sudo systemctl start mariadb

generate_password() {
    local length=$1
    local password=$(LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w "$length" | head -n 1)
    echo "$password"
}

mariadb_password=$(generate_password 12)

print_red "THE SCRIPT WANTS TO SECURE MARIADB PLEASE THE PASSWORD BELOW. CANNOT ADD IT MANUALLY. BELOW IS YOUR GENERATED PASSWORD. PLEASE SAVE IT SOMEWHERE AND ALWAYS USE IT WHEN ASKED FOR MARIAB PASSWORD DURING INSTALLATION THIS IS IMPORTANT!!!"
print_green "$mariadb_password"

print_green "CREATING INITIAL DATABASE. WHEN ASKED FOR PASSWORD USE THE ONE BELOW"
print_green "$mariadb_password"
sudo mariadb  <<EOF
CREATE DATABASE IF NOT EXISTS originality_app;
EOF

# Secure MariaDB installation
sudo mysql_secure_installation

print_green "FLUSHING MARIADB PRIVILEGES. WHEN ASKED FOR PASSWORD USE THE ONE BELOW"
print_green "$mariadb_password"
#flush tables
sudo mariadb  <<EOF
GRANT ALL ON *.* TO 'root'@'localhost' IDENTIFIED BY '$mariadb_password' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF





#-----------------------------------------------------------------------------------------------
#
# APPLICATION INSTALLER
#
#-----------------------------------------------------------------------------------------------


## SCRIPT INSTALLATION
#enable apache mod rewrite
sudo a2enmod rewrite

#install python-venv
sudo apt install python3.10-venv


#remove previous installations
sudo rm -r originality-integration-fiverr


# Clone the repository from GitHub
sudo git clone https://github.com/mashcom/originality-integration-fiverr

# Navigate to the cloned repository
cd originality-integration-fiverr

#create the .env file
sudo cp .env_example .env

#update .env database password
sed -i "s/^DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$mariadb_password/g" .env

# Create a directory for virtual environments
sudo mkdir .venvs

# Create a virtual environment for Django
sudo python3 -m venv venvs/django

# Activate the virtual environment
source venvs/django/bin/activate

# Create a log file for Django
sudo touch logs/django.log

# Set permissions for the log file
sudo chmod 0777 logs/django.log

# Change ownership of the repository to www-data user and group
sudo chown -R www-data:www-data .

# Set directory permissions
sudo chmod 0777 .

# Install Python dependencies
sudo venvs/django/bin/pip install -r requirements.txt


#-----------------------------------------------------------------------------------------------
#
# DATABASE CONFIGURATION
#
#-----------------------------------------------------------------------------------------------

# Run database migrations
print_green "CREATING MIGRATION"
sudo venvs/django/bin/python manage.py makemigrations

print_green "RUNNING MIGRATIONS"
sudo venvs/django/bin/python manage.py migrate

print_green "PLEASE ENTER THE CREDENTIALS OF SUPER ADMIN USER"
#create application super user
sudo venvs/django/bin/python manage.py createsuperuser

print_green "INSTALLATION COMPLETED BELOW IS YOUR MARIADB PASSWORD"

print_green $mariadb_password