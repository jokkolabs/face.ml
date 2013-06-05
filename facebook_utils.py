#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json

import requests

from utils import create_raw_from_url


def get_data_from_fql(query, token):
    url = 'https://graph.facebook.com/fql'
    params = {'q': query,
              'access_token': token}
    req = requests.get(url, params=params)
    if not req.status_code in (200, 201):
        return None
    try:
        return json.loads(req.text)
    except:
        return None


def find_jpeg_in(data, callback):

    def add_url(url):
        print('FOUND URL: %s' % url)
        callback(url)

    def walk(dl):
        if not isinstance(dl, (dict, list, tuple)):
            if unicode(dl).lower().endswith('.jpg'):
                add_url(dl)
            return
        iterator = [(None, e) for e in dl] \
            if isinstance(dl, (list, tuple)) else dl.items()
        for k, v in iterator:
            walk(v)
    walk(data)


def get_oid_from_aid(aid, token):
    query = "select owner from album where aid='%s'" % aid
    data = get_data_from_fql(query, token)
    return data.get("owner")


def get_username_from_owner_id(oid, token):
    query = "select username from user where uid='%s'" % oid
    data = get_data_from_fql(query, token)
    return data.get("username")


def get_username_from_aid(aid, token):
    return get_username_from_owner_id(get_oid_from_aid(aid, token), token)


def find_jpeg_in_album(data, token, username=None):
    print("called find_jpeg_in_album")

    def add_url(url):
        create_raw_from_url(url, username)

    def request_album_pics(aid):
        print("AID %s" % aid)
        fb_username = get_username_from_aid(aid, token)
        print("??????? %s" % fb_username)
        query = "select src_big from photo where aid='%s' LIMIT 5000" % aid
        find_jpeg_in_album(data=get_data_from_fql(query, token),
                           token=token,
                           username=fb_username)

    def walk(dl):
        if not isinstance(dl, (dict, list, tuple)):
            return
        iterator = [(None, e) for e in dl] \
            if isinstance(dl, (list, tuple)) else dl.items()
        for k, v in iterator:
            if k == 'aid':
                request_album_pics(v)
            if k == 'src_big':
                add_url(v)
            walk(v)
    walk(data)
