#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from flask import request

from utils import TAGS, _FACE_ID, LOGGED_IN
from tasks import execute_facebook_stream_processing
from utils.image_capture import get_data_from_fql
from utils.face_data import (get_current_winner, get_random_oponents,
                             get_face_from, do_face_refresh)
from utils.sessions import create_anonymous_session, user_ident_from_session, create_session
from utils.users import update_user_details, get_create_user_from
from views import success_response, error_response, require_user, session_response


def get_or_create_session():
    session_id = request.cookies.get('session_id')
    if session_id:
        user, _ = user_ident_from_session(session_id)
        if user:
            return session_response(session_id)
    return get_anonymous_session()


def get_anonymous_session():
    return session_response(create_anonymous_session(request))


# remove: updtae infos from token
# def update_facebook_user_details():

#     user_id = request.form.get('id')
#     user = get_create_user_from(user_id, user_type=LOGGED_IN)
#     user = update_user_details(user, request.form)
#     return success_response()


@require_user
def refresh(user):
    ''' returns the main page information refreshed

        params (GET): none

        returns:
            winner: winner picture obj
            left: a random picture obj
            right: a random picture obj
            remaining_votes: an int '''

    # user = get_create_user_from(request)
    favorites = user.get('favorites', [])

    winner = get_current_winner()
    left, right = get_random_oponents(update_views=True)

    # remaining_votes = get_remaining_votes(user)
    # response = {'winner': winner,
    #             'left': left,
    #             'right': right,
    #             'remaining_votes': remaining_votes}
    #             }
    response = {'left': left,
                'right': right,
                'favorites': favorites,
                'winner': winner,
                'all_tags': TAGS}
    return success_response(response)


@require_user
def face_refresh(user):
    face_id = request.form.get('face_id')
    if not face_id:
        return error_response("No `face_id`.")

    response = do_face_refresh(face_id, user)

    return success_response(response)


def process_user_stream():
    ''' Retrieves User's facebook wall pictures

        params (GET):
            token: facebook token

        returns: success '''
    token = request.args.get('token', None)
    if not token:
        return error_response(u"No TOKEN!", silent=True)
    print(token)

    user_infos = get_data_from_fql('/me', token, as_fql=False)

    user = get_create_user_from(user_infos.get('id'), user_type=LOGGED_IN)
    user = update_user_details(user, user_infos)
    from pprint import pprint as pp ; pp(user)

    execute_facebook_stream_processing.apply_async([token])

    session_id = create_session(user.get('ident'), user.get('type'))

    return session_response(session_id)
