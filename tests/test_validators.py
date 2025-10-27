import pytest

from src import validators


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

    args = validators.Arguments(
        action='deploy', 
        domain_name='example.com',
        source_dir='./source_dir'
    )
    args.validate_arguments()


def test_domain_name():
    """
    The domain_name argument must be set if action is set to deploy.
    """
    args = validators.Arguments(action='deploy')
    with pytest.raises(Exception):
        args.validate_arguments()

    args = validators.Arguments(
        action='deploy', 
        domain_name='example.com',
        source_dir='./source_dir'
    )
    args.validate_arguments()
