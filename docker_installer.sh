#!/bin/bash

# Update the package index and upgrade the system packages
sudo apt update
#sudo apt upgrade -y

# Install necessary packages to allow apt to use repositories over HTTPS
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add the official Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add the Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package index again
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io
a
# Verify Docker installation
sudo docker run hello-world

# Add current user to the docker group
sudo usermod -aG docker $USER

# Display a message to logout and log back in for the changes to take effect
echo "Please logout and log back in to use Docker without 'sudo'."


#installer docker composer

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose


sudo chmod +x /usr/local/bin/docker-compose

docker-compose --version

# End of script
