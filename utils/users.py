#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from utils import LOGGED_IN
from utils.database import Users


def get_create_user_from(user_id, user_type=LOGGED_IN):
    global Users
    user = Users.find_one({'type': user_type, 'ident': user_id})
    if not user:
        user_id = Users.insert({'type': user_type, 'ident': user_id})
        user = Users.find_one({'type': user_type, 'ident': user_id})
    return user


def update_user_details(user, data):
    global Users
    fb_data = {}
    for k, v in data.items():
        if not k in ('id'):
            fb_data.update({k: v})
    user.update(fb_data)
    Users.save(user)
    return user
