from transpose import *
import pytest


@pytest.fixture()
def transposed():
    parser = CParser(['tests/test.h'])
    enum_macros = create_enum_macros(parser)
    define_macros = create_define_macros(parser)
    return create_output('test.h', enum_macros, define_macros)


def test_main(transposed):
    with open('tests/expected_result.h', 'r') as reader:
        expected_result = reader.read()
    assert transposed == expected_result
