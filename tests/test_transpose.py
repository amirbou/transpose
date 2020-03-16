from transpose import *
import os
import subprocess
import shutil

SYSTEM_TEST_PATH = os.path.join('tests', 'system_test')


def do_transpose(path):
    parser = CParser([path])
    enum_macros = create_enum_macros(parser)
    define_macros = create_define_macros(parser)
    return create_output(os.path.basename(path), enum_macros, define_macros)


def compile_c(path, out_path):
    subprocess.run(['gcc', path, '-o', out_path], check=True)


def run_binary(path):
    return subprocess.run([path], capture_output=True).stdout


def test_main():
    transposed = do_transpose(os.path.join(SYSTEM_TEST_PATH, 'test.h'))
    with open(os.path.join(SYSTEM_TEST_PATH, 'expected_result.h'), 'r') as reader:
        expected_result = reader.read()
    assert transposed == expected_result


def test_in_c(tmpdir):
    main(os.path.join(SYSTEM_TEST_PATH, 'test.h'), tmpdir / 'result.h', [])
    shutil.copyfile(os.path.join(SYSTEM_TEST_PATH, 'test.h'), tmpdir / 'test.h')
    shutil.copyfile(os.path.join(SYSTEM_TEST_PATH, 'main.c'), tmpdir / 'main.c')
    compile_c(tmpdir / 'main.c', tmpdir / 'test.out')
    result = run_binary(tmpdir / 'test.out').decode('utf-8')
    with open(os.path.join(SYSTEM_TEST_PATH, 'expected_from_c'), 'r') as fd:
        expected = fd.read()
    assert result == expected
