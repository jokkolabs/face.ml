#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from flask import request

from views import success_response, error_response, require_user
from utils.users import create_favorite_for
from utils.face_data import add_tag_to_face, do_face_refresh, vote_for_face


@require_user
def add_face_to_favorite(user):
    face_id = request.form.get('face_id', None)
    if not face_id:
        return error_response("No face_id to fav.")
    create_favorite_for(user, face_id)
    return success_response(do_face_refresh(face_id, user))


@require_user
def tag_face(user):
    face_id = request.form.get('face_id', None)
    tag_id = request.form.get('tag_id', None)
    if not face_id or not tag_id:
        return error_response("Missing `tag_id` or `face_id")

    add_tag_to_face(face_id, tag_id, user)

    return success_response(do_face_refresh(face_id, user))


@require_user
def vote_face(user):
    face_id = request.form.get('face_id', None)
    if not face_id:
        return error_response("No face_id to vote for.")

    return success_response(vote_for_face(face=face_id, user=user))


# add favorite
# remove favorite
# vote favorite
# tag face
# Ajouter Bonus (used=False, type=BONUS+2, MALUS-1)
# AJouter ExtraVote (used=False)
