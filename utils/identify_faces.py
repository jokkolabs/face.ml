#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import uuid
import datetime

from utils import _FACE_ID, FACE_DONE, FACE_PICTURE, NOTTAGGED, _FACEBOOK_ID
from utils.database import FacePictures
from utils.raw_pictures import get_raw_picture_by, update_raw_picture
from utils.face_data import get_face_from


def delete_face(picture_id):
    global FacePictures
    FacePictures.remove({_FACE_ID: picture_id})
    return True


def mark_raw_picture_complete(facebook_id):
    ''' Moves a RawPicture from FACE_PICTURE to FACE_DONE '''
    return update_raw_picture(facebook_id, {'type': FACE_DONE})


def get_raw_picture_for_facing(facebook_id=None):
    ''' Get details of picture for facing or pick one if no request '''
    global RawPictures
    # this will either return the request picture or the first one avail.
    picture = get_raw_picture_by(facebook_id,
                                 extra_query={'type': FACE_PICTURE},
                                 select=['url', _FACEBOOK_ID, 'type'])
    if not picture is None:
        faces = get_faces_for_raw_picture(picture.get(_FACEBOOK_ID))
    else:
        faces = []
    return (picture, faces)


def create_single_face(facebook_id, x, y, width, height):
    raw_picture = get_raw_picture_by(facebook_id)
    picture = create_face_picture(raw_picture.get('url'),
                                  facebook_id, x, y, width, height)
    return picture


def create_face_picture(url, facebook_id, x, y, width, height):
    global FacePictures
    raw = get_raw_picture_by(facebook_id)
    face_id = uuid.uuid4().hex
    doc = {_FACE_ID: face_id,
           'url': url,
           'face_x': x,
           'face_y': y,
           'face_width': width,
           'face_height': height,
           'source_width': raw.get('width'),
           'source_height': raw.get('height'),
           'facebook_id': facebook_id,
           'datetime': datetime.datetime.now(),
           'nb_votes': 0,
           'nb_votes_total': 0,
           'tag': NOTTAGGED,
           'tags': {},
           'views': 0,
           'views_total': 0,
           'score': 0,
           'score_total': 0,
           'nb_favorited': 0,
           'favorite_votes': 0,
           'favorite_votes_total': 0,
           'bonusmalus': [],
           'bonusmalus_total': [],
           'has_won': False}
    FacePictures.insert(doc)
    return get_face_from(face_id)


def get_faces_for_raw_picture(facebook_id):
    return FacePictures.find({_FACEBOOK_ID: facebook_id})
