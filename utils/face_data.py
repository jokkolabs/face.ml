#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import random

from utils import _FACE_ID
from utils.database import FacePictures
from utils.computations import compute_score_for


def get_face_from(face_id, update_views=False):
    ''' return a FacePictures obj from `face_id` '''
    global FacePictures
    face = FacePictures.find_one({_FACE_ID: face_id})
    if update_views:
        add_one_view_to(face)
    return face


def update_face(face, data):
    global FacePictures
    face.update(data)
    FacePictures.save(face)


def get_current_winner():
    global FacePictures
    return FacePictures.find_one(sort={'score': -1}, limit=1)


def get_random_face(extra_query=None, update_views=False):
    global FacePictures
    cursor = FacePictures.find(extra_query)
    nb_faces = cursor.count()
    rand = random.randint(0, nb_faces - 1)
    try:
        face = cursor[rand:rand][0]
        add_one_view_to(face)
        return face
    except KeyError:
        return None


def get_random_oponents(update_views=False):
    left = get_random_face(update_views=update_views)
    right = get_random_face({_FACE_ID: {'$ne': left.get(_FACE_ID)}},
                            update_views=update_views)
    return (left, right)


def get_status_update():
    '''
        - remaining_votes
        - favorites
        - nb_tag_required_per_page '''
    pass


def get_gallery_faces(sort_order='-chrono', with_tags=None,
                      limit=9, user_id=None, page=0):
    '''

        sort_order:
            'chrono', '-chrono': chronological order
            'score', '-score': sorted by score

        add if user_id has tagged each picture'''
    global FacePictures
    if sort_order == '-chrono':
        sort_query = {'datetime': -1}
    elif sort_order == 'chrono':
        sort_query = {'datetime': 1}
    elif sort_order == '-score':
        sort_query = {'score': -1}
    elif sort_order == 'score':
        sort_query = {'score': 1}
    else:
        # default soring order
        sort_query = {'datetime': -1}

    query = {'tag': {'$in': with_tags}}

    return FacePictures.find(query,
                             sort=sort_query,
                             limit=limit,
                             skip=page * limit)


# is in user favorite?

def update_views_for(face_id):
    # add Views
    # Update FacePictures
    pass


def update_votes_for(face_id):
    # add Vote
    # Update FacePictures
    pass


def add_one_view_to(face):
    new_views = face.get('views', 0) + 1
    new_views_total = face.get('views_total', 0) + 1
    new_score = compute_score_for(face)
    update_face(face, {'views': new_views,
                       'views_total': new_views_total,
                       'score': new_score})
