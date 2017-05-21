# -*- coding: utf-8 -*-
"""
    flask_login._compat
    -------------------
    A module providing tools for cross-version compatibility.
    Code copied from: (https://github.com/maxcountryman/flask-login) See LICENSE
"""

import sys

PY2 = sys.version_info[0] == 2

if not PY2:  # pragma: no cover
    str = str  # needed for pyflakes in py3

if PY2:  # pragma: nocover


    def iteritems(d):
        return iter(d.items())


    def itervalues(d):
        return iter(d.values())


    text_type = str

else:  # pragma: nocover

    from urllib.parse import urlparse, urlunparse


    def iteritems(d):
        return iter(list(d.items()))


    def itervalues(d):
        return iter(list(d.values()))


    text_type = str

__all__ = [
    'PY2',
    'unicode',
    'urlparse',
    'urlunparse',
    'iteritems',
    'itervalues',
    'text_type',
]
