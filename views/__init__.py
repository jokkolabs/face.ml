#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from bson import json_util
from bson.json_util import dumps
from flask import request, Response

from utils.users import user_from_request
from utils.errors import ERROR_MESSAGES


def require_user(target_func):

    def wrapper():
        user = user_from_request(request)
        if user:
            return target_func(user)
        else:
            return error_response("Session has expired")
    # hack for Flask's app.route decorator
    wrapper.__name__ = target_func.__name__
    return wrapper


def success_response(data=None):
    response = {'status': 'success',
                'data': data}
    resp = Response(dumps(response, default=json_util.default),
                    mimetype='application/json')
    if isinstance(data, dict) and 'session_id' in data.keys():
        resp.set_cookie('session_id', data.get('session_id'))
    return resp


def error_response(message=None, code=None, silent=False):
    response = {'status': 'error',
                'message': message,
                'data': None}
    if message is None and code is not None:
        response.update({'message': ERROR_MESSAGES.get(code)})
    return Response(dumps(response, default=json_util.default),
                    mimetype='application/json')


def session_response(session_id):
    return success_response({'session_id': session_id})
