from unittest.mock import patch

from lib import commands


def test_calls_validate_arguments_method():
    with patch('lib.commands.validators.Arguments') as MockArguments:
        mock_arguments = MockArguments.return_value

        class Args:
            action = 'iam'

        commands.main(Args)
        mock_arguments.validate_arguments.assert_called_once_with(Args)
