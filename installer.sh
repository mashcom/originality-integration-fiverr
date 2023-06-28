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

print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
print_red "RUNNING THE SETUP, GODSPEED :-)"
print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"

# Update package lists
sudo apt-get -qq update

# Install necessary packages
yes | sudo apt-get install apache2
yes | sudo apt-get install apache2-dev
yes | sudo apt-get install build-essential
yes | sudo apt-get install python3-dev
yes | sudo apt-get install libapache2-mod-wsgi-py3
yes | sudo apt-get install libpq-dev
yes | sudo apt-get install netcat
yes | sudo apt-get install default-libmysqlclient-dev
yes | sudo apt-get install libmagic-dev

# Remove cached package lists
yes | sudo rm -rf /var/lib/apt/lists/*

# Update package lists again
yes | sudo apt-get update

#install snapd
yes | sudo apt update
yes | sudo apt install snapd
yes | sudo snap install core; sudo snap refresh core

#install certbot, this is used for SSL certificate generation and management
yes | sudo apt-get remove certbot
yes | sudo snap install --classic certbot
yes | sudo ln -s /snap/bin/certbot /usr/bin/certbot

print_green "INSTALLING MARIADB"
# Install MariaDB server
yes | sudo apt-get install mariadb-server

# Start MariaDB service
sudo systemctl start mariadb

generate_password() {
    local length=$1
    local password=$(LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w "$length" | head -n 1)
    echo "$password"
}

mariadb_password=$(generate_password 12)
print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
print_red "THE SCRIPT WANTS TO SECURE MARIADB PLEASE KEEP THE PASSWORD BELOW SOMEWHERE. BELOW IS YOUR GENERATED PASSWORD. PLEASE SAVE IT SOMEWHERE AND ALWAYS USE IT WHEN ASKED FOR MARIAB PASSWORD DURING INSTALLATION THIS IS IMPORTANT!!!"
print_green "$mariadb_password"
print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
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
yes | sudo a2enmod rewrite

yes | sudo a2enmod wsgi


#install python-venv
yes | sudo apt install python3.10-venv


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

sudo mkdir logs
sudo mkdir tokens
sudo mkdir uploads/assignments
# Create a log file for Django
sudo touch logs/django.log

# Set permissions for the log file
sudo chmod 0777 logs/django.log

# Change ownership of the repository to www-data user and group
sudo chown -R www-data:www-data .

# Set directory permissions
sudo chmod 0777 .

print_green "-------------------------------------------------------------"
print_green "INSTALLING DEPENDENCIES"
print_green "-------------------------------------------------------------"
# Install Python dependencies
sudo venvs/django/bin/pip install -r requirements.txt


#-----------------------------------------------------------------------------------------------
#
# DATABASE CONFIGURATION
#
#-----------------------------------------------------------------------------------------------

# Run database migrations
print_green "-------------------------------------------------------------"
print_green "CREATING MIGRATION"
print_green "-------------------------------------------------------------"
sudo venvs/django/bin/python manage.py makemigrations

print_green "-------------------------------------------------------------"
print_green "RUNNING MIGRATIONS"
print_green "-------------------------------------------------------------"
sudo venvs/django/bin/python manage.py migrate

print_green "-------------------------------------------------------------"
print_green "PLEASE ENTER THE CREDENTIALS OF SUPER ADMIN USER"
print_green "-------------------------------------------------------------"
#create application super user
sudo venvs/django/bin/python manage.py createsuperuser

print_green "-------------------------------------------------------------"
print_green "APACHE2 AND SSL CONFIGURATION"
print_green "-------------------------------------------------------------"
# Prompt the user to input the values of the variables
print_green -------------------------------------------------------------
print_green "PLEASE ENTER THE SERVER ADMIN EMAIL"
print_green -------------------------------------------------------------
read -p "Enter APPLICATION_SERVER_ADMIN: " APPLICATION_SERVER_ADMIN
print_green "-------------------------------------------------------------"
print_green "INSTALLATION COMPLETED BELOW IS YOUR MARIADB PASSWORD"
print_green "-------------------------------------------------------------"
exit
sudo service apache2 stop

print_green ------------------------------------------------------------------------------------------------------------------------------------------------------------------
print_green "PLEASE ENTER THE APPLICATION DOMAIN NAME. ENSURE THE DOMAIN NAME HAS NOT HTTP/HTTPS e.g example.com or originality.example.com if the application is on subdomain"
print_green ------------------------------------------------------------------------------------------------------------------------------------------------------------------
read -p "Enter APPLICATION_DOMAIN_NAME: " APPLICATION_DOMAIN_NAME

print_green -------------------------------------------------------------
print_green "RUNNING SSL INSTALLATION"
print_green -------------------------------------------------------------
sudo certbot certonly --standalone -d $APPLICATION_DOMAIN_NAME

# Set APPLICATION_ROOT_DIR to the current directory
APPLICATION_ROOT_DIR=$(pwd)

# Generate a random string with 12 characters for WSGID_PROCESS_NAME
WSGID_PROCESS_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)

# Specify the path to the Apache configuration template file
TEMPLATE_FILE="apache_example.conf"
SSL_TEMPLATE_FILE="apache_ssl_example.conf"

# Specify the path to the generated Apache configuration file
CONFIG_FILE="originality_apache.conf"
SSL_CONFIG_FILE="originality_apache_ssl.conf"

# Copy the template file to the new configuration file
cp "$TEMPLATE_FILE" "$CONFIG_FILE"
cp "$SSL_TEMPLATE_FILE" "$SSL_CONFIG_FILE"

# Replace the variables in the configuration file using envsubst
export APPLICATION_SERVER_ADMIN
export APPLICATION_DOMAIN_NAME
export APPLICATION_ROOT_DIR
export WSGID_PROCESS_NAME
envsubst < "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
mv "$CONFIG_FILE.tmp" "/etc/apache2/sites-available/$CONFIG_FILE"

echo "Configuration file generated: $CONFIG_FILE"

WSGID_PROCESS_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
# Replace the variables in the configuration file using envsubst
export APPLICATION_SERVER_ADMIN
export APPLICATION_DOMAIN_NAME
export APPLICATION_ROOT_DIR
export WSGID_PROCESS_NAME
envsubst < "$SSL_CONFIG_FILE" > "$SSL_CONFIG_FILE.tmp"
mv "$SSL_CONFIG_FILE.tmp" "/etc/apache2/sites-available/$SSL_CONFIG_FILE"

echo "Configuration file generated: $SSL_CONFIG_FILE"

sudo a2ensite originality_apache
sudo a2ensite originality_apache_ssl
sudo service apache2 restart

print_green "-------------------------------------------------------------"
print_green "INSTALLATION COMPLETED BELOW IS YOUR MARIADB PASSWORD"
print_green "-------------------------------------------------------------"
