import os


def test_cli():
    exit_status = os.system('./main.py')
    assert exit_status == 0
