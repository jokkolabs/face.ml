#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import uuid

import pylibmc

from utils import ANONYMOUS

SESSION_DELAY = 7200  # 2h

mc = pylibmc.Client(["127.0.0.1"],
                    binary=True,
                    behaviors={"tcp_nodelay": True, "ketama": True})


def create_session(user_id, user_type):
    session_id = uuid.uuid4().hex
    mc.set(session_id, "%s#%s" % (user_id, user_type), SESSION_DELAY)
    return session_id


def user_ident_from_session(session_id):
    try:
        user_id, user_type = mc.get(session_id).split('#', 1)
        return user_id, user_type
    except (TypeError, ValueError, AttributeError):
        return None, None


def create_anonymous_session(req):
    ip_addr = req.remote_addr
    return create_session(ip_addr, ANONYMOUS)


def add_to_cache(key, value):
    mc.set(str(key), value)


def get_from_cache(key):
    return mc.get(str(key))
