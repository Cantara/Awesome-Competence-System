FROM ubuntu:12.10
MAINTAINER Leon Ho

# Install dependencies for ACS installation
RUN apt-get update
RUN apt-get install -y python g++ make software-properties-common --force-yes

RUN apt-get install apache2
# In /etc/apache2/apache2.conf add ServerName altubutu01
RUN /etc/init.d/apache2 restart
# Fix certificates
RUN  make-ssl-cert generate-default-snakeoil --force-overwrite
# install mod_wsgi
RUN apt-get install libapache2-mod-wsgi
RUN apt-get install sqlite3
RUN apt-get install git
RUN sudo apt-get install openjdk-8-jdk openjdk-8-doc openjdk-8-source 

RUN adduser acs-user
RUN su -c acs user git clone https://github.com/altran/Awesome-Competence-System.git /home/acs-user/acs


RUN apt-get install python-django
COPY acs.conf /etc/apache2/sites-available/acs.conf


# Expose port 80 and 443 
EXPOSE 80 443
CMD ["npm","start"]


