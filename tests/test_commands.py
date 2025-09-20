from unittest.mock import patch

from src import commands


class Args:
    """
    Mock argparse.ArgumentParser object used for testing.
    """
    action = 'iam'


def test_calls_validate_arguments_method():
    with patch('src.commands.validators.Arguments') as MockArguments:
        mock_arguments = MockArguments.return_value

        commands.main(Args)

        mock_arguments.validate_arguments.assert_called_once_with()


def test_calls_create_iam_template_if_iam_action_is_specified():
    with patch('src.commands.iam') as MockIamModule:
        commands.main(Args)

        MockIamModule.create_iam_template.assert_called_once_with(
            'define_iam_user.yml'
        )
        assert MockIamModule.create_iam_template.call_count == 1

        Args.action = 'deploy'
        commands.main(Args)

        assert MockIamModule.create_iam_template.call_count == 1
