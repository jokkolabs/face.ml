#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import sys

from flask import Flask

from views.main import (get_or_create_session, refresh, process_user_stream, face_refresh)
from views.actions import (add_face_to_favorite, tag_face, vote_face)
from views.imam import (unknown_pictures_list,
                        confirm_raw_picture,
                        detach_raw_picture,
                        detach_face,
                        complete_raw_picture,
                        raw_picture_for_facing,
                        add_single_face)

abs_path = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(abs_path)
STATIC_DIR = os.path.join(ROOT_DIR, 'static')

app = Flask('static_server', static_folder=STATIC_DIR)
app.debug = True


@app.route('/')
def root():
    return open('face.html', 'r').read()


@app.route('/gallery')
def gallery():
    return open('gallery.html', 'r').read()


@app.route('/imam')
def imam():
    return open('imam.html', 'r').read()

app.route('/request_session')(get_or_create_session)
app.route('/fbget')(process_user_stream)
# app.route('/fbupdate', methods=['POST'])(update_facebook_user_details)
# app.route('/vote')(vote)
app.route('/refresh')(refresh)
app.route('/face_refresh', methods=['POST'])(face_refresh)

app.route('/all_unknown')(unknown_pictures_list)
app.route('/picture_facing')(raw_picture_for_facing)
app.route('/confirm_raw_picture', methods=['POST'])(confirm_raw_picture)
app.route('/detach_raw_picture', methods=['POST'])(detach_raw_picture)
app.route('/detach_face', methods=['POST'])(detach_face)
app.route('/add_single_face', methods=['POST'])(add_single_face)
app.route('/complete_raw_picture', methods=['POST'])(complete_raw_picture)

# ACTIONS
app.route('/add_to_fav', methods=['POST'])(add_face_to_favorite)
app.route('/tag_face', methods=['POST'])(tag_face)
app.route('/vote_face', methods=['POST'])(vote_face)


if __name__ == '__main__':
    try:
        http_port = int(sys.argv[1])
    except:
        http_port = 5000
    app.run(debug=True, port=http_port, host='0.0.0.0')
