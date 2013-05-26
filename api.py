#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from flask import request

from utils import (success_response, error_response,
                   get_remaining_votes, vote_for_a_pic, get_winner,
                   get_random_pictures, get_user_from,
                   create_raw_from_url, demongo_cursor
                   RawPictures, UNKNOWN, FACE_PICTURE, BAD_PICTURE)
from facebook_utils import get_data_from_fql, find_jpeg_in_album


def vote():
    ''' User submits a vote to a Picture

        params (GET):
            fb_username (optional)
            pic_id: UUID of the Picture

        returns: success '''

    user = get_user_from(request)
    pic_id = request.args.get('pic_id')
    did_vote = vote_for_a_pic(pic_id=pic_id, from_user=user)
    if did_vote:
        return success_response()
    else:
        return error_response(code='LIMIT_LOGGED_IN')


def refresh():
    ''' returns the main page information refreshed

        params (GET): none

        returns:
            winner: winner picture obj
            left: a random picture obj
            right: a random picture obj
            remaining_votes: an int '''

    user = get_user_from(request)
    winner = get_winner()
    left, right = get_random_pictures(limit=2)
    remaining_votes = get_remaining_votes(user)
    response = {'winner': winner,
                'left': left,
                'right': right,
                'remaining_votes': remaining_votes}
    return success_response(response)


def crawl_user_wall():
    ''' Retrieves User's facebook wall pictures

        params (GET):
            token: facebook token

        returns: success '''
    token = request.args.get('token', None)
    if not token:
        return error_response(u"No TOKEN!", silent=True)
    print('Received TOKEN: %s' % token)

    query = ("SELECT attachment FROM stream WHERE filter_key='others' "
             "OR filter_key='owner'")
    wall_data = get_data_from_fql(query, token)

    find_jpeg_in_album(data=wall_data, token=token,
                       callback=create_raw_from_url)

    return success_response()


def unknown_pictures_list():
    ''' JSON list of raw pictures for Step1 '''
    limit = request.args.get('limit', 20)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20
    dbreq = RawPictures.find(query={'type': UNKNOWN},
                             fields=['url', 'facebook_id'],
                             limit=limit,)
    return success_response(data=demongo_cursor(dbreq))


def confirm_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to FACE_PICTURE '''
    return confirm_or_detach_picture(request, FACE_PICTURE)


def detach_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to BAD_PICTURE '''
    return confirm_or_detach_picture(request, BAD_PICTURE)


def confirm_or_detach_picture(request, new_status):
    ''' Change the status of an UNKNOWN RawPicture based on request '''
    facebook_id = request.form.get('facebook_id', None)
    if not facebook_id:
        return error_response(u"`facebook_id` not found")

    raw_picture = RawPictures.find_one(query={'facebook_id': facebook_id})
    raw_picture.update({'type': new_status})
    RawPictures.save(raw_picture)

    return success_response(raw_picture)
