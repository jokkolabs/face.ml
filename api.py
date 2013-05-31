#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from flask import request

from utils import (success_response, error_response,
                   get_remaining_votes, vote_for_a_pic, get_winner,
                   get_random_pictures, get_user_from,
                   create_raw_from_url, demongo_cursor, demongo,
                   UNKNOWN, FACE_PICTURE, BAD_PICTURE, FACE_DONE,
                   RawPictures, Pictures,
                   create_picture_from, votes_for, ID)
from facebook_utils import get_data_from_fql, find_jpeg_in_album
from tasks import execute_facebook_crawl


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
    winner.update({'nb_votes': votes_for(winner.get(ID))})
    left.update({'nb_votes': votes_for(left.get(ID))})
    right.update({'nb_votes': votes_for(right.get(ID))})
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

    execute_facebook_crawl.apply_async([token])

    return success_response()


def unknown_pictures_list():
    ''' JSON list of raw pictures for Step1 '''
    limit = request.args.get('limit', 20)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20
    dbreq = RawPictures.find({'type': UNKNOWN},
                             fields=['url', 'facebook_id'],
                             limit=limit,)
    return success_response(data=demongo_cursor(dbreq))


def confirm_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to FACE_PICTURE '''
    # return confirm_or_detach_picture(request, FACE_PICTURE)
    facebook_id = request.form.get('facebook_id', None)
    try:
        picture_width = int(request.form.get('picture_width', None))
        picture_height = int(request.form.get('picture_height', None))
    except ValueError:
        return error_response("incorrect picture sizes")
    if not facebook_id:
        return error_response(u"`facebook_id` not found")

    raw_picture = RawPictures.find_one({'facebook_id': facebook_id})
    raw_picture.update({'type': FACE_PICTURE,
                        'width': picture_width,
                        'height': picture_height})
    RawPictures.save(raw_picture)
    return success_response(raw_picture)


def detach_raw_picture():
    ''' Moves a RawPicture from UNKNOWN to BAD_PICTURE '''
    facebook_ids = request.form.getlist('facebook_ids[]')
    if not facebook_ids:
        return error_response(u"`facebook_ids` not found")

    # print(facebook_ids)
    for facebook_id in facebook_ids:
        if not facebook_id:
            continue
        print("DELETING %s" % facebook_id)
        raw_picture = RawPictures.find_one({'facebook_id': facebook_id})
        raw_picture.update({'type': BAD_PICTURE})
        RawPictures.save(raw_picture)
    return success_response()


def detach_face():
    picture_id = request.form.get('picture_id')
    if not picture_id:
        return error_response(u"`picture_id` not found")

    print("DELETING %s" % picture_id)
    Pictures.remove({'picture_id': picture_id})
    return success_response()


def complete_raw_picture():
    ''' Moves a RawPicture from FACE_PICTURE to FACE_DONE '''
    facebook_id = request.form.get('facebook_id')
    if not facebook_id:
        return error_response(u"`facebook_id` not found")

    raw_picture = RawPictures.find_one({'facebook_id': facebook_id})
    if not raw_picture:
        return error_response("can't find raw pic with %s" % facebook_id)
    raw_picture.update({'type': FACE_DONE})
    RawPictures.save(raw_picture)
    return success_response(raw_picture)


def raw_picture_for_facing():
    ''' JSON RawPicture for Step2 '''

    picture = RawPictures.find_one({'type': FACE_PICTURE},
                                   fields=['url', 'facebook_id', 'type'])
    faces = Pictures.find({'facebook_id': picture.get('facebook_id')})

    return success_response({'picture': demongo(picture),
                             'faces': demongo_cursor(faces)})


def add_single_face():
    facebook_id = request.form.get('facebook_id', None)
    x = request.form.get('face_x', None)
    y = request.form.get('face_y', None)
    width = request.form.get('face_width', None)
    height = request.form.get('face_height', None)

    for v in (x, y, width, height):
        try:
            v = int(v)
        except ValueError:
            pass

    if facebook_id is None or x is None or y is None or width is None or height is None:
        return error_response("incorrect parameters")

    raw_picture = RawPictures.find_one({'facebook_id': facebook_id})

    picture = create_picture_from(raw_picture.get('url'),
                                  facebook_id, x, y, width, height)
    return success_response(demongo(picture))


# def gallery():
#     context = {"category": 'gallery'}

#     id_best = Best_imag.find_one().get('best')
#     best = Pictures.find_one({"_id": id_best})
#     context.update({"star": best})
#     return render_template('gallery.html', **context)


def pictures_for_gallery(*args, **kwargs):
    ''' JSON list of pictures for gallery '''
    pictures = Pictures.find(fields=['url', 'facebook_id'],)
    return success_response(data=demongo_cursor(pictures))
