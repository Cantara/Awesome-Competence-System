#!/bin/bash
python manage.py build_solr_schema > schema.xml.bli
sudo mv schema.xml.bli ../solr/solr/collection1/conf/schema.xml
sudo chown solr:solr ../solr/solr/collection1/conf/schema.xml
