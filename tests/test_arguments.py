import pytest

from .. import validators


def test_action_values():
    args = validators.Arguments()
    with pytest.raises(Exception):
        args.validate_arguments()

    args = validators.Arguments(action='false')
    with pytest.raises(Exception):
        args.validate_arguments()
