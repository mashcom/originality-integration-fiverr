#!/bin/bash

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
REQUIRED_VERSION="3.8"

# Compare versions
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Python version $REQUIRED_VERSION or higher is required."
    exit 1
fi

# Continue with your script here
echo "Python version is $PYTHON_VERSION. Proceeding..."


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

generate_password() {
    local length=$1
    local password=$(LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w "$length" | head -n 1)
    echo "$password"
}

print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
print_red "RUNNING THE SETUP, GODSPEED :-)"
print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"

# Remove cached package lists
yes | sudo rm -rf /var/lib/apt/lists/*

# Update package lists
sudo apt-get update

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

#install snapd
yes | sudo apt-get install snapd
yes | sudo snap install core; sudo snap refresh core

#install certbot, this is used for SSL certificate generation and management
yes | sudo apt-get remove certbot
yes | sudo snap install --classic certbot
yes | sudo ln -s /snap/bin/certbot /usr/bin/certbot

print_green "INSTALLING MARIADB"
# Install MariaDB server

mariadb_password=$(generate_password 12)
mariadb_username="root"
# Start MariaDB service

max_attempts=10
attempt=1
connected=false

while [ $attempt -le $max_attempts ] && [ $connected == false ]; do
    if command -v mysql &>/dev/null; then
        sudo systemctl start mariadb
        read -p "Enter the MariaDB username: " mariadb_username
        read -s -p "Enter the MariaDB password: " mariadb_password
        echo

        if mysql -u "$mariadb_username" -p"$mariadb_password" -e "quit" &>/dev/null; then
            connected=true
            echo "Successfully connected to MariaDB."
        else
            echo "Failed to connect to MariaDB. Attempt $attempt of $max_attempts."
            ((attempt++))
        fi
    else
    
        yes | sudo apt-get install mariadb-server
        sudo systemctl start mariadb

        print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        print_red "THE SCRIPT WANTS TO SECURE MARIADB"
        print_green "$mariadb_password"
        print_green "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        
        # Secure MariaDB installation
        sudo mysql_secure_installation

        sudo systemctl start mariadb
        read -p "Enter the MariaDB username: " mariadb_username
        read -s -p "Enter the MariaDB password: " mariadb_password
        echo

        if mysql -u "$mariadb_username" -p"$mariadb_password" -e "quit" &>/dev/null; then
            connected=true
            print_green "Successfully connected to MariaDB."
        else
            print_red "Failed to connect to MariaDB. Attempt $attempt of $max_attempts."
            ((attempt++))
        fi
    
    fi
done

if [ $connected == false ]; then
    print_red "Failed to establish a connection to MariaDB after $max_attempts attempts."
    exit
fi

while true; do
  read -p "Enter the name for the database (leave blank for default 'originality_app'): " database_name

  if [[ -z $database_name ]]; then
    database_name="originality_app"
    break
  elif [[ $database_name =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    break
  else
    echo "Invalid database name. Only alphanumeric characters and underscores are allowed. The name must start with a letter or underscore."
  fi
done

sudo mariadb -u "$mariadb_username" -p"$mariadb_password" <<EOF
CREATE DATABASE IF NOT EXISTS $database_name;
EOF

#flush tables
sudo mariadb -u "$mariadb_username" -p"$mariadb_password" <<EOF
GRANT ALL ON *.* TO '$mariadb_username'@'localhost' IDENTIFIED BY '$mariadb_password' WITH GRANT OPTION;
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
sed -i "s/^DATABASE_USERNAME=.*/DATABASE_USERNAME=$mariadb_username/g" .env
sed -i "s/^DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$mariadb_password/g" .env
sed -i "s/^DATABASE_NAME=.*/DATABASE_NAME=$database_name/g" .env

sed -i "s/^DEBUG=.*/DEBUG=False/g" .env

# Create a directory for virtual environments
sudo mkdir .venvs

# Create a virtual environment for Django
sudo python3 -m venv venvs/django

# Activate the virtual environment
source venvs/django/bin/activate

sudo mkdir logs
sudo mkdir tokens
sudo mkdir assets
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
print_green "CREATING MIGRATION"
sudo venvs/django/bin/python manage.py makemigrations

print_green "RUNNING MIGRATIONS"
sudo venvs/django/bin/python manage.py migrate

print_green "PLEASE ENTER THE CREDENTIALS OF APPLICATION SUPER ADMIN USER"
#create application super user
sudo venvs/django/bin/python manage.py createsuperuser

print_green "-------------------------------------------------------------"
print_green "APACHE2 AND SSL CONFIGURATION"
print_green "-------------------------------------------------------------"
# Prompt the user to input the values of the variables
# Function to validate if a variable has a value
validate_variable() {
  if [[ -z "$1" ]]; then
    print_green "ERROR: The variable $2 is empty."
    exit 1
  fi
}

print_green "PLEASE ENTER THE SERVER ADMIN EMAIL"
while true; do
  read -p "Enter APPLICATION_SERVER_ADMIN: " APPLICATION_SERVER_ADMIN
  validate_variable "$APPLICATION_SERVER_ADMIN" "APPLICATION_SERVER_ADMIN" && break
done

sudo service apache2 stop

print_green "PLEASE ENTER THE APPLICATION DOMAIN NAME. ENSURE THE DOMAIN NAME HAS NOT HTTP/HTTPS (e.g., example.com or originality.example.com if the application is on a subdomain)"
while true; do
  read -p "Enter APPLICATION_DOMAIN_NAME: " APPLICATION_DOMAIN_NAME
  validate_variable "$APPLICATION_DOMAIN_NAME" "APPLICATION_DOMAIN_NAME" && break
done

print_green -------------------------------------------------------------
print_green "Generating SSL certificate for domain  $APPLICATION_DOMAIN_NAME "
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
CONFIG_FILE=" 000-default.conf"
SSL_CONFIG_FILE="000-default-le-ssl.conf"

# Copy the template file to the new configuration file
cp "$TEMPLATE_FILE" "$CONFIG_FILE"
cp "$SSL_TEMPLATE_FILE" "$SSL_CONFIG_FILE"

#backup config
sudo cp /etc/apache2/sites-available/00-default.conf /etc/apache2/sites-available/00-default.conf.bak
sudo cp /etc/apache2/sites-available/000-default-le-ssl.conf /etc/apache2/sites-available/000-default-le-ssl.conf.bak

# Replace the variables in the configuration file using envsubst
export APPLICATION_SERVER_ADMIN
export APPLICATION_DOMAIN_NAME
export APPLICATION_ROOT_DIR
export WSGID_PROCESS_NAME
envsubst < "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
mv -f "$CONFIG_FILE.tmp" "/etc/apache2/sites-available/$CONFIG_FILE"

echo "Configuration file generated: $CONFIG_FILE"

WSGID_PROCESS_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
# Replace the variables in the configuration file using envsubst
export APPLICATION_SERVER_ADMIN
export APPLICATION_DOMAIN_NAME
export APPLICATION_ROOT_DIR
export WSGID_PROCESS_NAME
envsubst < "$SSL_CONFIG_FILE" > "$SSL_CONFIG_FILE.tmp"
mv -f "$SSL_CONFIG_FILE.tmp" "/etc/apache2/sites-available/$SSL_CONFIG_FILE"

echo "Configuration file generated: $SSL_CONFIG_FILE"

sudo a2ensite 000-default
sudo a2ensite 000-default-le-ssl
sudo service apache2 restart

print_green "-------------------------------------------------------------"
print_green "INSTALLATION COMPLETED"
print_green "Please visit https://$APPLICATION_DOMAIN_NAME/admin for administration (Recommended)"
print_green "Please visit https://$APPLICATION_DOMAIN_NAME for general application usage "
print_green "-------------------------------------------------------------"
