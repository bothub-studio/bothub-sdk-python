# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import traceback


def traceback_to_string(exc):
    s = traceback.extract_stack()[:-3] + traceback.extract_tb(exc.__traceback__)
    l = traceback.format_list(s)
    return ''.join(l) + '\\n  {} {}'.format(exc.__class__, exc)
