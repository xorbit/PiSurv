#!/bin/sh

# Package name
PACKAGE_NAME=pisurv
# Install directory
INSTALL_DIRECTORY=/usr/share/$PACKAGE_NAME

# Create the install and recordings directories
mkdir -p $INSTALL_DIRECTORY/templates
mkdir -p $INSTALL_DIRECTORY/config
mkdir -p /var/lib/$PACKAGE_NAME

# Copy the Python source files
install -p *.py $INSTALL_DIRECTORY
# Byte-compile the sources
python -m compileall $INSTALL_DIRECTORY
# Copy the templates directory
install -p templates/* $INSTALL_DIRECTORY/templates
# Copy the config directory
install -p config/* $INSTALL_DIRECTORY/config

# Set the install directory in the init script
sed -i "s:INSTALL_DIRECTORY:$INSTALL_DIRECTORY:" $INSTALL_DIRECTORY/config/init
# Create a symbolic link to the init script
rm /etc/init.d/$PACKAGE_NAME
ln -s $INSTALL_DIRECTORY/config/init /etc/init.d/$PACKAGE_NAME

# Enable the service to start on boot
update-rc.d $PACKAGE_NAME defaults
# Restart the service
service $PACKAGE_NAME restart

# Create a symbolic link to the Nginx config
rm /etc/nginx/sites-enabled/$PACKAGE_NAME
ln -s $INSTALL_DIRECTORY/config/nginx /etc/nginx/sites-enabled/$PACKAGE_NAME
# Restart Nginx
service nginx restart

