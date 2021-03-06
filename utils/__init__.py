#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

# default tag
NOTTAGGED = "NOTTAGGED"

# Raw Pictures Types
UNKNOWN = 'UNKNOWN'
FACE_PICTURE = 'FACE_PICTURE'
BAD_PICTURE = 'BAD_PICTURE'
FACE_DONE = 'FACE_DONE'


# types of User
LOGGED_IN = 'LOGGED_IN'
ANONYMOUS = 'ANONYMOUS'

# Vote types
REGULAR = 'REGULAR'
FAVORITE = 'FAVORITE'

# Type of Views
VOTEPAGE = 'VOTEPAGE'
FAVORITEPAGE = 'FAVORITEPAGE'
GALLERY = 'GALLERY'

# Voting limits for User
MAX_VOTES_LOGGED_IN = 10
MAX_VOTES_ANONYMOUS = 3

NB_MAX_FAVORITES = 9
NB_MAX_VOTES_FAVORITES = 1

# Mongo DB field index
_FACE_ID = 'face_id'
_FROM = 'from'
_FROM_TYPE = 'from_type'
_FACEBOOK_ID = 'facebook_id'

# Tags
TAGS = {
    'sexy': "Sexy",
    'vulgar': "Vulgaire",
    'not_natural': "Chacho !"
}


def now():
    return datetime.datetime.now()


def today():
    return datetime.date.today()


def ensure_face(target_func):

    def wrapper(*args, **kwargs):
        from utils.face_data import get_face_from
        face = kwargs.get('face', None)
        if face is None:
            raise Exception("@ensure_face decorator needs explicit face.")

        if not isinstance(face, dict):
            kwargs['face'] = get_face_from(face)

        return target_func(*args, **kwargs)

    return wrapper
