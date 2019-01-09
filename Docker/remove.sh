#!/bin/sh
echo stopping ACS
docker stop ACS
echo removing ACS
docker rm ACS
echo list active docker containers
docker ps
