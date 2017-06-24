import os
import subprocess
import sys


def test_flake8():
    """Test source code for pyFlakes and PEP8 conformance"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(this_dir, '..', 'ebuild_generator')
    cmd = [sys.executable, '-m', 'flake8', source_dir, '--count']
    # if flake8_import_order is installed, set the style to google
    try:
        import flake8_import_order  # noqa
        cmd.extend(['--import-order-style=google'])
    except ImportError:
        pass
    # work around for https://gitlab.com/pycqa/flake8/issues/179
    cmd.extend(['--jobs', '1'])
    if sys.version_info < (3, 4):
        # Unless Python3, skip files with new syntax, like `yield from`
        cmd.append('--exclude={0}/*async_execute_process_asyncio/impl.py'.format(source_dir))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    print(stdout)
    assert p.returncode == 0, \
        "Command '{0}' returned non-zero exit code '{1}'".format(' '.join(cmd), p.returncode)
