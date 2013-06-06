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
