#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

import requests

from utils.raw_pictures import create_raw_from_url


def get_data_from_fql(query, token, as_fql=True):
    """ Get the JSON result of an FQL request """
    params = {'access_token': token}
    url = 'https://graph.facebook.com'
    if as_fql:
        url += '/fql'
        params.update({'q': query})
    else:
        url += query
    req = requests.get(url, params=params)
    if not req.status_code in (200, 201):
        return None
    try:
        return json.loads(req.text)
    except:
        return None


def extract_image_urls_from_fbdata(data, token):
    def add_url(url, url_small=None, owner=None):
        print("trying to add %s" % url)
        create_raw_from_url(url, url_small, owner)

    def request_album_pics(aid):
        query = "select src_small, src_big, owner from photo where aid='%s' " \
                "LIMIT 5000" % aid
        extract_image_urls_from_fbdata(data=get_data_from_fql(query, token),
                                       token=token)

    def walk(dl):
        if not isinstance(dl, (dict, list, tuple)):
            return
        iterator = [(None, e) for e in dl] \
            if isinstance(dl, (list, tuple)) else dl.items()
        for k, v in iterator:
            if k == 'aid':
                request_album_pics(v)
            if k == 'src_big':
                add_url(v, dl.get('src_small'), dl.get('owner'))
            walk(v)
    walk(data)
