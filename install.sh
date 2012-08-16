#!/bin/sh
# Install CV application in a python virtualenv.

# First, grab systemwide stuff we need.
sudo apt-get install libapache2-mod-wsgi python-django virtualenv python-<virtualenv python-virtualenv build-essential libxml2-dev libxslt-dev python-dev libjpeg-dev libpng-dev python-psycopg2
sudo apt-get remove python-imaging

# PIL might not find these libraries on 64-bit systems,
# so we symlink them manually to have PIL support JPEGs.
sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/
sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/
sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/

# Set up virtualenv and grab the application dependencies
virtualenv deps
source deps/bin/activate
pip install django appy.pod django-webodt pil reportlab requests

# Appy.pod does not have the right package at PyPI, so we grab it manually
wget https://launchpad.net/appy/0.8/0.8.0/+download/appy0.8.0.zip -O /tmp/appy.zip
unzip /tmp/appy.zip -d deps/lib/python2.6/site-packages/
rm /tmp/appy.zip

# Done!
echo
echo "*** FINISHED ***"
echo
