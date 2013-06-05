#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from utils import MAX_VOTES_ANONYMOUS, MAX_VOTES_LOGGED_IN

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
