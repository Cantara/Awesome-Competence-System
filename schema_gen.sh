#!/bin/bash
python manage.py build_solr_schema > schema.xml.bli
sudo mv schema.xml.bli /home/solr/solr/collection1/conf/schema.xml
sudo chown solr:solr /home/solr/solr/collection1/conf/schema.xml
