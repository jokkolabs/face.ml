#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
from bson import json_util

from flask import request, Response

from tasks import execute_facebook_stream_processing
from utils import LOGGED_IN
from utils.errors import ERROR_MESSAGES
from utils.face_data import get_current_winner, get_random_oponents
from utils.raw_pictures import (list_raw_pictures_unknown,
                                 mark_bad_raw_picture,
                                 mark_raw_picture_confirmed)
from utils.identify_faces import (delete_face, get_raw_picture_for_facing,
                                  mark_raw_picture_complete, create_single_face)
from utils.users import get_create_user_from, update_user_details


def success_response(data=None):
    response = {'status': 'success',
                'data': data}
    return Response(json.dumps(response, default=json_util.default),
                    mimetype='application/json')


def error_response(message=None, code=None, silent=False):
    response = {'status': 'error',
                'message': message}
    if message is None and code is not None:
        response.update({'message': ERROR_MESSAGES.get(code)})
    return Response(json.dumps(response, default=json_util.default),
                    mimetype='application/json')


def update_facebook_user_details():

    user_id = request.form.get('id')
    user = get_create_user_from(user_id, user_type=LOGGED_IN)
    user = update_user_details(user, request.form)
    return success_response()


def refresh():
    ''' returns the main page information refreshed

        params (GET): none

        returns:
            winner: winner picture obj
            left: a random picture obj
            right: a random picture obj
            remaining_votes: an int '''

    # user = get_user_from(request)
    # winner = get_current_winner()
    # left, right = get_random_oponents()
    # remaining_votes = get_remaining_votes(user)
    # response = {'winner': winner,
    #             'left': left,
    #             'right': right,
    #             'remaining_votes': remaining_votes}
    #             }
    response = {}
    return success_response(response)


def process_user_stream():
    ''' Retrieves User's facebook wall pictures

        params (GET):
            token: facebook token

        returns: success '''
    token = request.args.get('token', None)
    if not token:
        return error_response(u"No TOKEN!", silent=True)

    execute_facebook_stream_processing.apply_async([token])

    return success_response()


def unknown_pictures_list():
    ''' JSON list of raw pictures for Step1 '''
    limit = request.args.get('limit', 20)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20

    return success_response(data=list_raw_pictures_unknown(limit=limit))


def confirm_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to FACE_PICTURE '''
    facebook_id = request.form.get('facebook_id', None)
    try:
        picture_width = int(request.form.get('picture_width', None))
        picture_height = int(request.form.get('picture_height', None))
    except ValueError:
        return error_response("incorrect picture sizes")

    if not facebook_id:
        return error_response(u"`facebook_id` not found")

    return success_response(mark_raw_picture_confirmed(facebook_id,
                                                       picture_width,
                                                       picture_height))


def detach_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to BAD_PICTURE '''
    facebook_ids = request.form.getlist('facebook_ids[]')
    if not facebook_ids:
        return error_response(u"`facebook_ids` not found")

    # print(facebook_ids)
    for facebook_id in facebook_ids:
        if not facebook_id:
            continue
        mark_bad_raw_picture(facebook_id)

    return success_response()


def detach_face():
    face_id = request.form.get('face_id')
    if not face_id:
        return error_response(u"`face_id` not found")

    delete_face(face_id)
    return success_response()


def complete_raw_picture():
    ''' Moves a RawPicture from FACE_PICTURE to FACE_DONE '''
    facebook_id = request.form.get('facebook_id')
    if not facebook_id:
        return error_response(u"`facebook_id` not found")

    mark_raw_picture_complete(facebook_id)
    return success_response()


def raw_picture_for_facing():
    ''' JSON RawPicture for Step2 '''

    picture, faces = get_raw_picture_for_facing()

    return success_response({'picture': picture,
                             'faces': faces})


def add_single_face():
    facebook_id = request.form.get('facebook_id', None)
    x = request.form.get('face_x', None)
    y = request.form.get('face_y', None)
    width = request.form.get('face_width', None)
    height = request.form.get('face_height', None)

    for v in (x, y, width, height):
        try:
            v = int(v)
        except ValueError:
            pass

    if facebook_id is None or x is None or y is None or width is None or height is None:
        return error_response("incorrect parameters")

    face = create_single_face(facebook_id, x, y, width, height)
    return success_response(face)
