FROM ubuntu:12.04
MAINTAINER Leon Ho

# Install dependencies for ACS installation
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y  python-software-properties wget


RUN apt-get install -y apache2
# In /etc/apache2/apache2.conf add ServerName altubutu01
RUN /etc/init.d/apache2 restart
# Fix certificates
RUN  make-ssl-cert generate-default-snakeoil --force-overwrite
# install mod_wsgi
RUN apt-get install -y libapache2-mod-wsgi
RUN ln -s /etc/apache2/mods-available/proxy.conf /etc/apache2/mods-enabled/proxy.conf
RUN ln -s /etc/apache2/mods-available/proxy.load /etc/apache2/mods-enabled/proxy.load
RUN /etc/init.d/apache2 restart

RUN apt-get install -y sqlite3
RUN apt-get install -y git
RUN apt-get install -y postfix
ENV DEBIAN_FRONTEND noninteractive

# Apache OpenOffice
# RUN add-apt-repository ppa:upubuntu-com/office
# RUN apt-get update
# RUN apt-get install -y unzip bzip2
# RUN apt-get install -y openoffice
# Install OpenOffice
RUN apt-get install -y libxt6
RUN apt-get install -y libxrender1

RUN wget http://sourceforge.net/projects/openofficeorg.mirror/files/4.1.1/binaries/en-US/Apache_OpenOffice_4.1.1_Linux_x86-64_install-deb_en-US.tar.gz
RUN tar -xvf Apache_OpenOffice*.tar.gz
RUN dpkg -i en-US/DEBS/*.deb
RUN dpkg -i en-US/DEBS/desktop-integration/*.deb


# Azul OpenJDK
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9
RUN apt-add-repository "deb http://repos.azulsystems.com/ubuntu stable main"
RUN apt-get update 
# RUN apt-get install -y  zulu-8

#Install Oracle Java 8
# RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list
# RUN echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-add-repository "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main"
# RUN apt-add-repository "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main"
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
RUN apt-get update
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true |  /usr/bin/debconf-set-selections
RUN apt-get install -y oracle-java8-installer


# ACS stuff
RUN adduser acs-user
RUN  su -  acs-user -c  "git clone https://github.com/altran/Awesome-Competence-System.git "
RUN  su -  acs-user -c  "ln -s Awesome-Competence-System acs" 


# SOLR
RUN adduser solr
RUN su -  solr -c "/usr/bin/wget -O /home/solr/solr-4.4.0.tgz -q -N  https://archive.apache.org/dist/lucene/solr/4.4.0/solr-4.4.0.tgz"
RUN su -  solr -c "tar -zxvf solr-4.4.0.tgz"

RUN apt-get install -y python-django
ADD acs.conf /etc/apache2/sites-available/acs.conf
RUN ln -s /etc/apache2/sites-available/acs.conf /etc/apache2/sites-enabled/acs.conf
ADD .htaccess /home/acs-user/.htaccess
ADD .htaccess /home/acs-user/password

RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

RUN apt-get install -y libgtk2.0-0:i386 libidn11:i386 libglu1-mesa:i386
# Expose port 80 and 443 
EXPOSE 80 443
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN ln -s /etc/supervisor/conf.d/supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord"]


