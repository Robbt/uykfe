#!/bin/bash

virtualenv3 -p /usr/local/bin/python3.2 --no-site-packages env
. env/bin/activate
cd stagger-read-only
python setup.py build
python setup.py install
easy_install sqlalchemy
easy_install altgraph
easy_install networkx
