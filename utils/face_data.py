#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import random

from utils import (_FACE_ID, now, ensure_face, NOTTAGGED,
                   REGULAR, ANONYMOUS, FAVORITE)
from utils.database import FacePictures, TaggedFace, Votes, Users
from utils.computations import compute_score_for
from utils.sessions import get_from_cache, add_to_cache


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


def get_current_winner(from_cache=True):
    if not from_cache:
        global FacePictures
        return FacePictures.find_one(sort={'score': -1}, limit=1)
    return get_from_cache('winner')


@ensure_face
def is_winner(face):
    # check if the passed face_id is the same of the winner.
    is_current_winner = (face.get(_FACE_ID) == get_from_cache('winner_id'))
    if not is_current_winner:
        return face.get('score', 0) > get_from_cache('winner_score')
    return True


def update_winner_cache_if_winner(face):
    if is_winner(face=face.get(_FACE_ID)):
        update_winner_cache(face)


def update_winner_cache(winner):
    # store winner's dict into MC
    add_to_cache('winner', winner)
    add_to_cache('winner_id', winner.get(_FACE_ID))
    add_to_cache('winner_score', winner.get('score'))


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
    # maybe update winner cache
    update_winner_cache_if_winner(face)


def add_one_vote_to(face, vote_type=REGULAR):
    key = 'nb_votes' if vote_type == REGULAR else 'favorite_votes'
    new_votes = face.get(key, 0) + 1
    new_votes_total = face.get('%s_total' % key, 0) + 1
    new_score = compute_score_for(face)
    update_face(face, {key: new_votes,
                       '%s_total' % key: new_votes_total,
                       'score': new_score})
    # maybe update winner cache
    update_winner_cache_if_winner(face)


def add_tag_to_face(face_id, tag_id, user):
    # check if user already tagged with same tag
    global TaggedFace
    global FacePictures
    if TaggedFace.find({'from': user.get('ident'),
                       _FACE_ID: face_id,
                       'tag': tag_id}).count():
        return False
    # create tag object
    TaggedFace.insert({'from': user.get('ident'),
                       'from_type': user.get('type'),
                       _FACE_ID: face_id,
                       'tag': tag_id,
                       'datetime': now()})

    face = get_face_from(face_id)

    # update face tags list
    face.update({'tags': face_tags_dict_for(face=face)})

    # maybe update main tag of face
    face.update({'tag': main_tag_for(face=face)})

    # save face
    FacePictures.save(face)

    # maybe update winner cache
    update_winner_cache_if_winner(face)


@ensure_face
def face_tags_dict_for(face):
    global TaggedFace

    agg_tags = TaggedFace.aggregate([
        {'$match': {_FACE_ID: face.get(_FACE_ID)}},
        {'$group': {'_id': "$tag",
                    'count': {'$sum': 1}}}]).get('result')

    tags = {}
    for td in agg_tags:
        tags.update({td.get('_id'): td.get('count')})
    return tags


@ensure_face
def main_tag_for(face):
    # get key for index = index() of .values()' max
    try:
        return face.get('tags', {}).keys()[face.get('tags', {}).values().index(max(face.get('tags', {}).values()))]
    except (KeyError, ValueError):
        return NOTTAGGED


def do_face_refresh(face_id, user):
    face = get_face_from(face_id, update_views=False)
    favorites = user.get('favorites', [])

    response = {
        _FACE_ID: face.get(_FACE_ID),
        'tags': face.get('tags'),
        'tag': face.get('tag'),
        'nb_favorited': face.get('nb_favorited'),
        'favorites': favorites,
    }

    return response


def user_can_vote(user, vote_type=REGULAR):
    ''' Checks if a `user` can vote based on NB of votes today

        returns if it can or not (bool) '''
    if user.get('type') == ANONYMOUS and vote_type == FAVORITE:
        return False
    key = 'nb_remaing_votes_%s' % vote_type.lower()
    return bool(user.get(key, 0))


def decrease_vote_counter(user, vote_type=REGULAR):
    global Users
    key = 'nb_remaing_votes_%s' % 'regular' if vote_type == REGULAR else 'favorite'
    user.update({key: user.get(key, 1) - 1})
    Users.save(user)


@ensure_face
def vote_for_face(face, user, vote_type=REGULAR):
    global Votes

    # verifie user can vote
    if not user_can_vote(user):
        return False

    # ajoute vote
    doc = {_FACE_ID: face.get(_FACE_ID),
           'from': user.get('ident'),
           'from_type': user.get('type'),
           'type': vote_type,
           'datetime': now()}
    Votes.insert(doc)

    # update vote counter sur facepicture
    add_one_vote_to(face)

    # decrease vote counter of user
    decrease_vote_counter(user, vote_type)

    # update winner?
    update_winner_cache_if_winner(face)



# def vote_for_a_pic(pic_id, from_user):
#     ''' register a vote to a `pic_id` from a `user`

#         returns whether vote was accepted (bool) '''
#     global Votes
#     if not can_vote(from_user):
#         return False

#     doc = {ID: pic_id,
#            'from': from_user.ident,
#            'from_type': from_user.type,
#            'datetime': datetime.now()}
#     Votes.insert(doc)
#     maybe_update_winner(pic_id)
#     return True



# def calcul_votes_for_user(user, day=None):
#     ''' Number of votes a User made

#         Either Total or for a `day` '''
#     global Votes
#     query = {'from': user.ident, 'from_type': user.type}
#     if not day is None:
#         sod = datetime(day.year, day.month, day.day)
#         eod = datetime(day.year, day.month, day.day, 23, 59, 59)
#         query.update({'datetime': {'$gte': sod.isoformat(),
#                                    '$lt': eod.isoformat()}})
#     return Votes.find(query).count()

# def votes_for(pic_id):
#     ''' Number of Votes for a particular Picture '''
#     global Votes
#     return Votes.find({ID: pic_id}).count()