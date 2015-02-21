FROM ubuntu:12.04
MAINTAINER Leon Ho

# Install dependencies for ACS installation
RUN apt-get update
RUN apt-get upgrade
RUN apt-get install -y  python-software-properties


RUN apt-get install -y apache2
# In /etc/apache2/apache2.conf add ServerName altubutu01
RUN /etc/init.d/apache2 restart
# Fix certificates
RUN  make-ssl-cert generate-default-snakeoil --force-overwrite
# install mod_wsgi
RUN apt-get install -y libapache2-mod-wsgi
RUN apt-get install -y sqlite3
RUN apt-get install -y git
RUN apt-get install -y postfix

# Apache OpenOffice
RUN add-apt-repository ppa:upubuntu-com/office
RUN apt-get update
RUN apt-get install -y unzip bzip2
RUN apt-get install -y openoffice


# Azul OpenJDK
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9
RUN apt-add-repository "deb http://repos.azulsystems.com/ubuntu stable main"
RUN apt-get update 
RUN apt-get install -y  zulu-8



# ACS stuff
RUN adduser acs-user
RUN  su -  acs-user -c  "git clone https://github.com/altran/Awesome-Competence-System.git "



#SOLR
RUN apt-get install -y  wget
RUN adduser solr
RUN su -  solr -c "/usr/bin/wget -O /home/solr/solr-4.4.0.tgz -q -N  https://archive.apache.org/dist/lucene/solr/4.4.0/solr-4.4.0.tgz"
RUN su -  solr -c "tar -zxvf solr-4.4.0.tgz"

RUN apt-get install -y python-django
ADD acs.conf /etc/apache2/sites-available/acs.conf
ADD .htaccess /home/acs-user/.htaccess
ADD .htaccess /home/acs-user/password

RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

# Expose port 80 and 443 
EXPOSE 80 443
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]


