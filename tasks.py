#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from celery import Celery

from utils import create_raw_from_url
from facebook_utils import get_data_from_fql, find_jpeg_in_album

celery = Celery(broker='mongodb://localhost:27017/celery')


@celery.task
def execute_facebook_crawl(token):
    query = ("SELECT attachment FROM stream WHERE filter_key='others' "
             "OR filter_key='owner' LIMIT 5000")
    wall_data = get_data_from_fql(query, token)

    find_jpeg_in_album(data=wall_data, token=token)
