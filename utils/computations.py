#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import math


def calcul_score_from_data(votes=0, views=0, favorited=0, favorite_votes=0,
                           bonusmalus=[]):

    # votes sont plus importants
    # ensuite favorisage
    # ensuite votes dans favoris
    coef_vote = 4
    coef_favorited = 3
    coef_favorite_votes = 2

    # votes sont sanctionnés par les vues
    try:
        s1 = votes**2 / views
    except ZeroDivisionError:
        s1 = 0

    # votes
    s1 = s1 * coef_vote

    # favorisages
    s2 = favorited * coef_favorited

    # votes favoris
    s3 = favorite_votes * coef_favorite_votes

    # score intermediaire
    s = s1 + s2 + s3

    # bonus are on top of score
    # bonusmalus is a list of (weight, number)
    for weight, number in bonusmalus:
        s += (weight * number)

    return math.ceil(s)


def compute_score_for(face):
    views = face.get('views', 0)
    votes = face.get('votes', 0)
    favorited = face.get('nb_favorited', 0)
    favorite_votes = face.get('favorite_votes', 0)
    bonusmalus = face.get('bonusmalus', [])

    return calcul_score_from_data(votes=votes, views=views,
                                  favorited=favorited,
                                  favorite_votes=favorite_votes,
                                  bonusmalus=bonusmalus)


def get_main_tag_for(face_id):
    pass


def get_tags_for(face_id):
    ''' list of tags used '''
    pass
