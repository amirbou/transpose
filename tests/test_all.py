#! /usr/bin/env python
import pytest
from transpose import *


def test_find_prefixes():
    subject = [
                Define('PF_X', '0x1'),
                Define('PF_W', '0x2'),
                Define('PF_R', '0x4'),
                Define('PF_MASKOS', '0x0ff00000'),
                Define('PF_MASKPROC', '0xf0000000'),
                Define('PT_GNU_RELRO', '0x6474e552'),
                Define('STB_LOOS', '10'),
                Define('STB_HIOS', '12'),
                Define('STB_LOPROC', '13'),
                Define('STB_HIPROC', '15'),
                Define('SHF_MERGE', '0x10'),
                Define('SHF_STRINGS', '0x20'),
                Define('SHF_INFO_LINK', '0x40'),
                Define('SHF_LINK_ORDER', '0x80'),
                Define('SHF_OS_NONCONFORMING', '0x100'),
                Define('SHF_GROUP', '0x200'),
                Define('SHF_TLS', '0x400'),
                Define('SHF_COMPRESSED', '0x800'),
                Define('SHF_MASKOS', '0x0ff00000'),
                Define('SHF_MASKPROC', '0xf0000000'),
                Define('PFB_BLA', '0xffffffff')
                ]
    prefixes, no_prefix = find_prefixes(subject)
    no_prefix = [define.name for define in no_prefix]
    assert sorted(list(prefixes.keys())) == sorted(['PF', 'STB', 'SHF']) and sorted(no_prefix) == sorted(['PT_GNU_RELRO', 'PFB_BLA'])


def test_merge_prefixes_no_collisions():
    subject = {
        'PF': [
            Define('PF_X', '0x1'),
            Define('PF_W', '0x2'),
            Define('PF_R', '0x4'),
            Define('PF_MASKOS', '0x0ff00000'),
            Define('PF_MASKPROC', '0xf0000000')
        ],
        'STB': [
            Define('STB_LOOS', '10'),
            Define('STB_HIOS', '12'),
            Define('STB_LOPROC', '13'),
            Define('STB_HIPROC', '15')
        ],
        'SHF': [
            Define('SHF_MERGE', '0x10'),
            Define('SHF_STRINGS', '0x20'),
            Define('SHF_GROUP', '0x200'),
            Define('SHF_TLS', '0x400'),
            Define('SHF_COMPRESSED', '0x800'),
            Define('SHF_MASKOS', '0x0ff00000'),
            Define('SHF_MASKPROC', '0xf0000000'),
            Define('SHF_LINK_ORDER', '0x80'),
            Define('SHF_OS_NONCONFORMING', '0x100')
        ],
        'SHF_INFO': [
            Define('SHF_INFO_LINK', '0x40'),
            Define('SHF_INFO_LOL', '0x41')
        ]
    }
    prefixes = merge_prefixes(subject)
    assert sorted(list(prefixes.keys())) == sorted(['PF', 'STB', 'SHF'])


def test_merge_prefixes_collisions():
    subject = {
        'PF': [
            Define('PF_X', '0x1'),
            Define('PF_W', '0x2'),
            Define('PF_R', '0x4'),
            Define('PF_MASKOS', '0x0ff00000'),
            Define('PF_MASKPROC', '0xf0000000')
        ],
        'STB': [
            Define('STB_LOOS', '10'),
            Define('STB_HIOS', '12'),
            Define('STB_LOPROC', '13'),
            Define('STB_HIPROC', '15')
        ],
        'SHF': [
            Define('SHF_MERGE', '0x10'),
            Define('SHF_STRINGS', '0x20'),
            Define('SHF_GROUP', '0x200'),
            Define('SHF_TLS', '0x400'),
            Define('SHF_COMPRESSED', '0x800'),
            Define('SHF_MASKOS', '0x0ff00000'),
            Define('SHF_MASKPROC', '0xf0000000'),
            Define('SHF_LINK_ORDER', '0x80'),
            Define('SHF_OS_NONCONFORMING', '0x100')
        ],
        'SHF_INFO': [
            Define('SHF_INFO_LINK', '0x40'),
            Define('SHF_INFO_LOL', '0x10')
        ]
    }
    prefixes = merge_prefixes(subject)
    assert sorted(list(prefixes.keys())) == sorted(['PF', 'STB', 'SHF', 'SHF_INFO'])



