#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from utils import (LOGGED_IN, NB_MAX_FAVORITES, now, _FACE_ID,
                   MAX_VOTES_LOGGED_IN, MAX_VOTES_ANONYMOUS,
                   NB_MAX_VOTES_FAVORITES)
from utils.database import Users, Favorites
from utils.sessions import user_ident_from_session
from utils.face_data import update_face, get_face_from, update_winner_cache_if_winner


def user_from_request(req):
    session_id = req.args.get('session_id', None)
    if not session_id:
        session_id = req.form.get('session_id', None)

    if session_id:
        user_id, user_type = user_ident_from_session(str(session_id))
        # session expired
        if not user_id:
            return None
        return get_create_user_from(user_id=user_id, user_type=user_type)
    return None


def user_from_user_id(user_id):
    global Users
    return Users.find_one({'ident': user_id})


def get_create_user_from(user_id, user_type=LOGGED_IN):
    global Users
    user = Users.find_one({'type': user_type, 'ident': user_id})
    if not user:
        max_votes_regular = MAX_VOTES_LOGGED_IN if user_type == LOGGED_IN else MAX_VOTES_ANONYMOUS
        Users.insert({'type': user_type, 'ident': user_id,
                      'nb_remaing_votes_regular': max_votes_regular,
                      'nb_remaing_votes_favorite': NB_MAX_VOTES_FAVORITES})
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


def favorites_ids_for_user(user):
    global Favorites
    return Favorites.find({'user_id': user.get('ident')})


def create_favorite_for(user, face_id):
    global Favorites
    global Users

    if face_id in user.get('favorites', []):
        return False

    if user.get('nb_favorited') >= NB_MAX_FAVORITES:
        return False

    # create favorite object
    Favorites.insert({_FACE_ID: face_id,
                      'user_id': user.get('ident'),
                      'datetime': now()})

    # update facepicture counter for favorites
    face = get_face_from(face_id)
    update_face(face, {'nb_favorited': face.get('nb_favorited', 0) + 1})

    # update user counter + list of favs
    user.update({'favorites': user.get('favorites', []) + [face_id, ]})
    Users.save(user)

    # maybe update winner cache
    update_winner_cache_if_winner(face)
