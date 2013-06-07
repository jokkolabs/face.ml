#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from flask import request

from views import success_response, error_response
from utils.raw_pictures import (list_raw_pictures_unknown,
                                mark_bad_raw_picture,
                                mark_raw_picture_confirmed)
from utils.identify_faces import (delete_face, get_raw_picture_for_facing,
                                  mark_raw_picture_complete, create_single_face)


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
