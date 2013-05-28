#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import sys

from flask import Flask

from api import (crawl_user_wall, vote, refresh, unknown_pictures_list,
                 confirm_raw_picture, detach_raw_picture,
                 raw_picture_for_facing, add_single_face,
                 complete_raw_picture)

# app = Flask('face_server')
# app.debug = True
import os
abs_path = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(abs_path)
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
app = Flask('static_server', static_folder=STATIC_DIR)
app.debug = True


@app.route('/')
def root():
    return open('face.html', 'r').read()


@app.route('/imam')
def imam():
    return open('imam.html', 'r').read()

app.route('/fbget')(crawl_user_wall)
app.route('/vote')(vote)
app.route('/refresh')(refresh)
app.route('/all_unknown')(unknown_pictures_list)
app.route('/picture_facing')(raw_picture_for_facing)
app.route('/confirm_raw_picture', methods=['POST'])(confirm_raw_picture)
app.route('/detach_raw_picture', methods=['POST'])(detach_raw_picture)
app.route('/add_single_face', methods=['POST'])(add_single_face)
app.route('/complete_raw_picture', methods=['POST'])(complete_raw_picture)

if __name__ == '__main__':
    try:
        http_port = int(sys.argv[1])
    except:
        http_port = 5000
    app.run(debug=True, port=http_port, host='0.0.0.0')
