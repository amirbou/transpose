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


def test_parse_macros_values():
    subject = {
        'A': '0x1',
        'B': '0x2',
        'C': '0x4',
        'D': '0x0ff00000',
        'E': '0xf0000000',
        'F': '10',
        'G': '~1',
        'H': '3 & 1',
        'I': '1 | 2',
        'J': '0x10',
        'K': '0x800',
        'L': '0x0ff00000',
        'M': 'J + I',
        'N': 'M + 1',
        'O': 'P + 2',
        'P': 'N',
        'Q': '1 << 4',
        'R': '1>> 2',
        'S': '2 >> 1'
    }
    expected = {
        'A': 0x1,
        'B': 0x2,
        'C': 0x4,
        'D': 0x0ff00000,
        'E': 0xf0000000,
        'F': 10,
        'G': -2,
        'H': 3 & 1,
        'I': 1 | 2,
        'J': 0x10,
        'K': 0x800,
        'L': 0x0ff00000,
        'Q': 1 << 4,
        'R': 1 >> 2,
        'S': 2 >> 1,
    }
    expected['M'] = expected['J'] + expected['I']
    expected['N'] = expected['M'] + 1
    expected['P'] = expected['N']
    expected['O'] = expected['P'] + 2
    
    parse_macros_values(subject)
    assert subject == expected

@pytest.mark.parametrize('subject, expected', [('a_', 'a'), ('a_b', 'a'), ('a_b_', 'a_b'), ('a_b_c', 'a_b')])
def test_strip_underscore(subject, expected):
    assert strip_underscore(subject) == expected

def test_hack_fix_hex_values():
    subject = {
        'A': '0x1',
        'B': '0x2',
        'C': '0x4',
        'D': '0x0ff00000',
        'E': '0xf0000000',
        'F': '10',
        'G': '12',
        'H': '13',
        'I': '15',
        'J': '0x10',
        'K': '0x800',
        'L': '0x0ff00000',
        'M': 'J + I',
        'N': 'M + 1',
        'O': 'P + 2',
        'P': 'N',
    }
    expected = {
        'A': '0x\'1\'',
        'B': '0x\'2\'',
        'C': '0x\'4\'',
        'D': '0x\'0ff00000\'',
        'E': '0x\'f0000000\'',
        'F': '10',
        'G': '12',
        'H': '13',
        'I': '15',
        'J': '0x\'10\'',
        'K': '0x\'800\'',
        'L': '0x\'0ff00000\'',
        'M': 'J + I',
        'N': 'M + 1',
        'O': 'P + 2',
        'P': 'N',
    }
    assert hack_fix_hex_values(subject) == expected
     

def create_guess_type_params(values, expected_type):
    return ([Define('A', value) for value in values], expected_type)

guess_type_params = [
    ([100, 50],'uint8_t'),
    ([100, -50], 'int8_t'),
    ([150, -50], 'int16_t'),
    ([300,], 'uint16_t'),
    ([60000, -1], 'int32_t'),
    ([70000,], 'uint32_t'),
    ([1, -200], 'int16_t'),
    ([1<<129, ], None),
    ([255,], 'uint8_t'),
    ([256,], 'uint16_t'),
]

@pytest.mark.parametrize('subject, expected', [create_guess_type_params(*param) for param in guess_type_params])
def test_guess_type(subject, expected):
    assert guess_type(subject) == expected