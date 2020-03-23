#! /usr/bin/env python
import pytest
from transpose import *


def test_merge_enumee():
    enumees = [
        Enumee('LOG_ID_MIN', 0),
        Enumee('LOG_ID_MAIN', 0),
        Enumee('LOG_ID_RADIO', 1),
        Enumee('LOG_ID_EVENTS', 2),
        Enumee('LOG_ID_SYSTEM', 3),
        Enumee('LOG_ID_CRASH', 4),
        Enumee('LOG_ID_STATS', 5),
        Enumee('LOG_ID_SECURITY', 6),
        Enumee('LOG_ID_KERNEL', 7),
        Enumee('LOG_ID_MAX', 8)
    ]
    enum = MacroCreator('LOG_ID', enumees)
    expected_result = {
        'LOG_ID_MIN_OR_MAIN': Enumee('LOG_ID_MIN', 0),
        'LOG_ID_RADIO': Enumee('LOG_ID_RADIO', 1),
        'LOG_ID_EVENTS': Enumee('LOG_ID_EVENTS', 2),
        'LOG_ID_SYSTEM': Enumee('LOG_ID_SYSTEM', 3),
        'LOG_ID_CRASH': Enumee('LOG_ID_CRASH', 4),
        'LOG_ID_STATS': Enumee('LOG_ID_STATS', 5),
        'LOG_ID_SECURITY': Enumee('LOG_ID_SECURITY', 6),
        'LOG_ID_KERNEL': Enumee('LOG_ID_KERNEL', 7),
        'LOG_ID_MAX': Enumee('LOG_ID_MAX', 8)
    }
    assert enum._merge_cdefs() == expected_result



