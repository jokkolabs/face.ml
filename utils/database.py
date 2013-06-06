#!/usr/bin/env python
# encoding=utf-8

import copy

from pymongo import MongoClient

from utils import _FACE_ID, _FROM, _FROM_TYPE


mongo_client = MongoClient('localhost', 27017)
db = mongo_client["face_db2"]


# def demongo(obj):
#     ''' removes `_id` key from a mongo object

#         Saves bandwidth since we don't use it '''
#     nobj = copy.deepcopy(obj)
#     try:
#         del nobj['_id']
#     except (KeyError, TypeError):
#         pass
#     return nobj


# def demongo_cursor(cursor):
#     return [demongo(obj) for obj in cursor]


""" RawPictures - Facebook source image

    - can contain face or not.
    - useful RawPictures have {type: FACE_PICTURE} or {type: FACE_DONE}
    - useless ones have {type: BAD_FACE}
    - default (on creation) have {type: UNKNOWN}
    - fields:
        - url:  full URL of JPEG image on facebook
        - type: filter on status (see above)
        - facebook_id: a unique identifier to that picture on facebook.
        - facebook_owner: Facebook UID of the owner of the picture
        - url_thumbnail: thumbnail (src_small) of the JPEG image on FB. """
RawPictures = db['raw_pictures']
RawPictures.ensure_index('url', unique=True, sparse=True)
RawPictures.ensure_index('facebook_id', unique=True, sparse=True)

""" FacePicture - An identified valid face

    - fields:
        - face_id: Unique identifier of that face
        - url: URL of the original size JPEG file on FB.
        - face_x: x coordinate of the face in the picture
        - face_y: y coordinate of the face in the picture
        - face_width: with of the face in the picture
        - face_height: height of the face in the picture
        - source_width: width of the original image on FB.
        - source_height: height of the original image on FB.
        - facebook_id: Unique ID of that pcture on FB.
        - datetime: Creation date

        - nb_votes: the total number of vote for the current period
        - nb_votes_total: total number of votes for all times.
        - tag: a string representing the dominant tag
        - tags: a dict of (tag: number) with all tags set and number of hits
        - views: number of views for the current period
        - views_total: number of views for all times.
        - score: score for the current period
        - score_total: score for all times.
        - nb_favorited: nb of people who has it in favorites
        - favorite_votes:
        - favorite_votes_total:
        - bonusmalus:
        - bonusmalus_total:
        - has_won: a boolean to exclude some pictures (winners)
        - win_period:
        - win_score:
        - win_views:
        - win_votes: """
FacePictures = db['face_pictures']
FacePictures.ensure_index('increment', unique=True, sparse=True)
FacePictures.ensure_index(_FACE_ID, unique=True, sparse=True)

""" Votes - A vote for a picture

    - fields:
        - face_id: unique face ID
        - from: FB id or IP address
        - from_type: ANONYMOUS or LOGGED_IN
        - type: REGULAR, FAVORITE
        - datetime: time of the vote """
Votes = db['votes']
Votes.ensure_index(_FROM)
Votes.ensure_index(_FROM_TYPE)
Votes.ensure_index(_FACE_ID)
Votes.ensure_index('type')

""" TaggedFace - A catoegorization of a picture

    - fields:
        - face_id: unique face ID
        - tag: one of the existing Tags
        - datetime:
        - from: Identified user
        - from_type: ANONYMOUS or LOGGED_IN """
TaggedFace = db['tagged_face']
TaggedFace.ensure_index(_FROM)
TaggedFace.ensure_index(_FROM_TYPE)
TaggedFace.ensure_index(_FACE_ID)

""" Views - A visitor saw the picture

    - fields:
        - face_id: unique face ID
        - from: FB id or IP address
        - from_type: ANONYMOUS or LOGGED_IN
        - type: VOTEPAGE, FAVORITEPAGE, GALLERY
        - datetime: time of the vote """
Views = db['views']
Views.ensure_index(_FROM)
Views.ensure_index(_FROM_TYPE)
Views.ensure_index(_FACE_ID)
Views.ensure_index('type')

""" Periods - A wining-periods

    -fields:
        - voting_start: votes open (Monday morning)
        - voting_end: votes closes (Friday 1pm)
        - final_start: finals open (Friday 2pm)
        - final_end: finals closes (Sunday 2pm)
        - break_start: no votes (Sunday 2pm)
        - break_end: end of period (Sunday 12am)
        - period_id: Week number
        - period_name:  """
Periods = db['periods']

""" Events - An event triggering actions

    - fields:
        - start:
        - end:
        - type:
        - """
Events = db['events']


""" Users - An identified

    fields:
        - type: ANONYMOUS or LOGGED_IN
        - ident: IP or FB id
        - various facebook data
        - nb_favorited: number of favs used
        - favorites = [] """
Users = db['users']

""" Favorites - A face favorited by a user

    fields:
        - face_id
        - user_id
        - datetime """
Favorites = db['favorites']
