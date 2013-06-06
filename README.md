face.ml
=======

A Facebook's danger sensibilization website


Installation
============

* sudo apt-get install mongodb memcached libmemcached-dev
* pip install -r requirements.txt
* LIBMEMCACHED=/usr easy_install pylibmc

Running
=======
* mongod
* celery -A tasks worker
* memcached
