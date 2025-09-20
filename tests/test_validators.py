import pytest

from lib import validators


def test_action_values():
    """
    The action argument must be either iam or deploy.
    """
    args = validators.Arguments()
    with pytest.raises(Exception):
        args.validate_arguments()

    args = validators.Arguments(action='false')
    with pytest.raises(Exception):
        args.validate_arguments()

    args = validators.Arguments(action='iam')
    args.validate_arguments()

    args = validators.Arguments(action='deploy')
    args.validate_arguments()
