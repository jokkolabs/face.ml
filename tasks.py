#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from celery import Celery

from utils.image_capture import (get_data_from_fql,
                                 extract_image_urls_from_fbdata)

celery = Celery(broker='mongodb://localhost:27017/celery')


@celery.task
def execute_facebook_stream_processing(token):
    query = ("SELECT attachment FROM stream WHERE filter_key='others' "
             "OR filter_key='owner' LIMIT 5000")
    wall_data = get_data_from_fql(query, token)

    extract_image_urls_from_fbdata(data=wall_data, token=token)
