from transpose import *
import os
import subprocess
import shutil
import sys

SYSTEM_TEST_PATH = os.path.join('tests', 'system_test')


def do_transpose(path, verbose = False):
    parser = CParser([path])
    enum_macros = create_enum_macros(parser.defs['enums'], verbose=verbose)
    define_macros = create_define_macros(parser.defs['macros'], verbose=verbose)
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
    main(os.path.join(SYSTEM_TEST_PATH, 'test.h'), tmpdir / 'result.h', macros=[],
         recursive=False, parse_std=False, compiler='gcc', include_dirs=[], max_headers=20, force=False, dry_run=False)
    shutil.copyfile(os.path.join(SYSTEM_TEST_PATH, 'test.h'), tmpdir / 'test.h')
    shutil.copyfile(os.path.join(SYSTEM_TEST_PATH, 'main.c'), tmpdir / 'main.c')
    result = ""
    try:
        compile_c(tmpdir / 'main.c', tmpdir / 'test.out')
        result = run_binary(tmpdir / 'test.out').decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        print(e.stdout)
    assert result
    with open(os.path.join(SYSTEM_TEST_PATH, 'expected_from_c'), 'r') as fd:
        expected = fd.read()
    assert result == expected

def test_list(capsys):
    expected = """Created inline function: logpriority_parser(enum LogPriority n)
Created inline function: log_id_parser(enum log_id n)
Created macro: DF_MAX_LEN (14)
Created macro: DF_PARSER(n, buf)
Created macro: DF_1_MAX_LEN (15)
Created macro: DF_1_PARSER(n, buf)
"""

    do_transpose(os.path.join(SYSTEM_TEST_PATH, 'test.h'), verbose=True)

    captured = capsys.readouterr().err
    assert captured == expected
