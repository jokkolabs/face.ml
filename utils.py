#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import json
import uuid
import random
import copy
from datetime import datetime, date

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import json_util
from flask import Response

# Pictures types
GENERATED = 'GENERATED'
ACCEPTED = 'ACCEPTED'
REFUSED = 'REFUSED'

# Raw Pictures Types
UNKNOWN = 'UNKNOWN'
FACE_PICTURE = 'FACE_PICTURE'
BAD_PICTURE = 'BAD_PICTURE'
FACE_DONE = 'FACE_DONE'


# types of User
LOGGED_IN = 'LOGGED_IN'
ANONYMOUS = 'ANONYMOUS'

# Voting limits for User
MAX_VOTES_LOGGED_IN = 10
MAX_VOTES_ANONYMOUS = 3

# Mongo DB field index
ID = 'picture_id'

# Error messages strings
ERROR_MESSAGES = {
    'LIMIT_GENERIC': u"Vous ne pouvez plus voter aujourd'hui: "
                     u"Les votes sont limités à %d votes/ jour pour "
                     u"les personnes identifiées via Facebook"
                     u"et %d votes / jour pour ceux qui ne sont "
                     u"pas identifiés" % (MAX_VOTES_LOGGED_IN,
                                          MAX_VOTES_ANONYMOUS),
    'LIMIT_LOGGED_IN': u"Vous ne pouvez plus voter aujourd'hui: les votes "
                       u"sont limités à %d par jour!" % MAX_VOTES_LOGGED_IN,
    'LIMIT_ANONYMOUS': u"Vous ne pouvez plus voter aujourd'hui: les votes "
                       u"sont limités à %d par jour!" % MAX_VOTES_ANONYMOUS}

mongo_client = MongoClient('localhost', 27017)
db = mongo_client["face_db"]

RawPictures = db['raw_pictures']
Votes = db['votes']
Cache = db['cache']
Pictures = db['pictures']

## setup indexes
# index + uniqueness on raw URLs
RawPictures.ensure_index('url', unique=True, sparse=True)
RawPictures.ensure_index('facebook_id', unique=True, sparse=True)
Pictures.ensure_index('random', unique=True, sparse=True)
Pictures.ensure_index(ID, unique=True, sparse=True)
# index on from votes
Votes.ensure_index('from')
Votes.ensure_index(ID)


def success_response(data=None):
    response = {'status': 'success',
                'data': data}
    return Response(json.dumps(response, default=json_util.default),
                    mimetype='application/json')


def error_response(message=None, code=None, silent=False):
    response = {'status': 'error',
                'message': message}
    if message is None and code is not None:
        response.update({'message': ERROR_MESSAGES.get(code)})
    return Response(json.dumps(response, default=json_util.default),
                    mimetype='application/json')


def demongo(obj):
    ''' removes `_id` key from a mongo object

        Saves bandwidth since we don't use it '''
    nobj = copy.deepcopy(obj)
    try:
        del nobj['_id']
    except KeyError:
        pass
    return nobj


def demongo_cursor(cursor):
    return [demongo(obj) for obj in cursor]


class User(dict):
    ''' User model to provide shortcuts for type and ident '''

    @property
    def type(self):
        return self.get('type')

    @property
    def ident(self):
        return self.get('ident')


def get_user_from(req):
    ip_addr = req.remote_addr
    fb_username = req.args.get('fb_username', None)
    if fb_username:
        return User({'type': LOGGED_IN, 'ident': fb_username})
    return User({'type': ANONYMOUS, 'ident': ip_addr})


def get_winner():
    ''' returns the Picture obj of the winner '''
    global Cache
    global Pictures
    try:
        winner_id = Cache.find_one({'name': 'winner_id'}).get(ID)
    except AttributeError:
        winner_id = get_random_object(Pictures, {}).get(ID)
    return get_picture_from(winner_id)


def get_picture_from(pic_id):
    ''' return a Picture obj from `pic_id` '''
    global Pictures
    return demongo(Pictures.find_one({ID: pic_id}))


def create_picture_from(url, facebook_id, x, y, width, height, auto=False):
    global Pictures
    global RawPictures
    raw = RawPictures.find_one({'facebook_id': facebook_id})
    pic_id = uuid.uuid4().hex
    doc = {ID: pic_id,
           'url': url,
           'face_x': x,
           'face_y': y,
           'face_width': width,
           'face_height': height,
           'source_width': raw.get('width'),
           'source_height': raw.get('height'),
           'facebook_id': facebook_id,
           'random': random.random(),
           'auto': auto,
           }
    Pictures.insert(doc)
    return get_picture_from(pic_id)


def create_raw_from_url(url):
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
        x = RawPictures.insert({'url': url, 'type': UNKNOWN,
                                'facebook_id': facebook_id})
        print('Accepted URL: %s' % url)
        return x
    except DuplicateKeyError:
        return False


def get_random_object(collection, query):
    rand = random.random()
    querya = copy.deepcopy(query)
    querya.update({'random': {'$gte': rand}})
    result = collection.find_one(querya)
    if not result:
        queryb = copy.deepcopy(query)
        queryb.update({'random': {'$lte': rand}})
        result = collection.find_one(queryb)
    return demongo(result)


def get_random_pictures(limit=2, valid=True):
    global Pictures
    picture_list = []
    for _ in xrange(limit):
        picture_list.append(get_random_object(Pictures, {}))
    return picture_list


def votes_for_user(user, day=None):
    ''' Number of votes a User made

        Either Total or for a `day` '''
    global Votes
    query = {'from': user.ident, 'from_type': user.type}
    if not day is None:
        sod = datetime(day.year, day.month, day.day)
        eod = datetime(day.year, day.month, day.day, 23, 59, 59)
        query.update({'datetime': {'$gte': sod.isoformat(),
                                   '$lt': eod.isoformat()}})
    return Votes.find(query).count()


def get_remaining_votes(user):
    ''' Number of remaining votes for a User '''
    limit = MAX_VOTES_LOGGED_IN if user.type == LOGGED_IN \
        else MAX_VOTES_ANONYMOUS
    return limit - votes_for_user(user)


def maybe_update_winner(pic_id):
    ''' Update the Cache winner if `pic_id` has more votes

        Returns whether it did update (bool) '''
    global Votes
    global Cache
    nb_votes = Votes.count({ID: pic_id})
    winner = Cache.find_one({'name': 'winner_id'})
    nb_votes_winner = Votes.count({ID: winner.get(ID)})
    if nb_votes > nb_votes_winner:
        winner.update({ID: pic_id})
        Cache.save(winner)
        return True
    return False


def vote_for_a_pic(pic_id, from_user):
    ''' register a vote to a `pic_id` from a `user`

        returns whether vote was accepted (bool) '''
    global Votes
    if not can_vote(from_user):
        return False

    doc = {ID: pic_id,
           'from': from_user.ident,
           'from_type': from_user.type,
           'datetime': datetime.now()}
    Votes.insert(doc)
    maybe_update_winner(pic_id)
    return True


def can_vote(user):
    ''' Checks if a `user` can vote based on NB of votes today

        returns if it can or not (bool) '''
    today = date.today()
    nb_votes = votes_for_user(user, day=today)
    nb_max = MAX_VOTES_LOGGED_IN if user.type == LOGGED_IN \
        else MAX_VOTES_ANONYMOUS
    return nb_votes < nb_max


def votes_for(pic_id):
    ''' Number of Votes for a particular Picture '''
    global Votes
    return Votes.find({ID: pic_id}).count()
