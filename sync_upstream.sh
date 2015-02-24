#!/bin/bash
git remote add upstream https://github.com/altran/Awesome-Competence-System.git
git fetch upstream
git merge upstream/master
git push
