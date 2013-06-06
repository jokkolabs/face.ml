#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from pymongo.errors import DuplicateKeyError

from utils import UNKNOWN, FACE_PICTURE, BAD_PICTURE, _FACEBOOK_ID
from utils.database import RawPictures


def create_raw_from_url(url, url_small=None, owner_id=None):
    ''' Create a RawPicture correctly initialized from a URL.

        Rejects non facebook.

        returns: success (bool) '''
    global RawPictures

    # reject non JPG
    if not url.endswith('.jpg'):
        return False

    # reject non Facebook pictures
    # reject profile pictures
    if not url.startswith('https://fbcdn-sphotos'):
        return False

    # extract photo ID
    try:
        facebook_id = url.rsplit('.jpg', 1)[0].rsplit('/', 1)[-1]
    except IndexError:
        facebook_id = None

    # reject non facebook ?
    if not facebook_id:
        return False

    try:
        x = RawPictures.insert({'url': url,
                                'type': UNKNOWN,
                                _FACEBOOK_ID: facebook_id,
                                'facebook_owner': owner_id,
                                'url_thumbnail': url_small})
        print('Accepted URL: %s' % url)
        return x
    except DuplicateKeyError:
        return False


def get_raw_picture_by(facebook_id, extra_query=None, select=None):
    global RawPictures
    query = {}
    if facebook_id:
        query.update({_FACEBOOK_ID: facebook_id})
    if extra_query:
        query.update(extra_query)
    raw_picture = RawPictures.find_one(query, fields=select)
    if not raw_picture:
        return False
    return raw_picture


def update_raw_picture(facebook_id, update_query):
    global RawPictures
    raw_picture = get_raw_picture_by(facebook_id)
    if not raw_picture:
        return False
    raw_picture.update(update_query)
    RawPictures.save(raw_picture)
    return True


def list_raw_pictures_unknown(limit=20):
    global RawPictures
    dbreq = RawPictures.find({'type': UNKNOWN},
                             fields=['url', 'url_thumbnail', _FACEBOOK_ID],
                             limit=limit)
    return dbreq


def mark_raw_picture_confirmed(facebook_id, picture_width, picture_height):
    global RawPictures
    # TODO: check width and height boundaries
    raw_picture = RawPictures.find_one({_FACEBOOK_ID: facebook_id})
    raw_picture.update({'type': FACE_PICTURE,
                        'width': picture_width,
                        'height': picture_height})
    RawPictures.save(raw_picture)
    return raw_picture


def mark_bad_raw_picture(facebook_id):
    return update_raw_picture(facebook_id, {'type': BAD_PICTURE})
