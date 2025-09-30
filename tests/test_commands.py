from unittest.mock import patch, MagicMock

from src import commands, create


class Args:
    """
    Mock argparse.ArgumentParser object used for testing.
    """
    action = 'iam'
    domain = 'example.com'


def test_calls_validate_arguments_method():
    with patch('src.commands.validators.Arguments') as MockArguments:
        mock_arguments = MockArguments.return_value

        commands.main(Args)

        mock_arguments.validate_arguments.assert_called_once_with()


@patch('src.commands.create')
def test_calls_create_iam_template_if_iam_action_is_specified(mock_module):
    with patch('src.commands.iam') as MockIamModule:
        Args.action = 'iam'

        commands.main(Args)

        MockIamModule.create_iam_template.assert_called_once_with(
            'define_iam_user.yml'
        )
        assert MockIamModule.create_iam_template.call_count == 1

        Args.action = 'deploy'
        commands.main(Args)

        assert MockIamModule.create_iam_template.call_count == 1


def test_calls_create_static_website_if_deploy_action_is_specified():
    with patch('src.commands.create') as MockModule:
        Args.action = 'iam'

        commands.main(Args)

        assert MockModule.create_static_website.call_count == 0

        Args.action = 'deploy'
        commands.main(Args)

        assert MockModule.create_static_website.call_count == 1
        MockModule.create_static_website.assert_called_once_with(
            'example.com'
        )


def test_calls_deploy_static_site_if_deply_action_is_specified():
    with patch('src.commands.create') as MockModule:
        mock_object = MagicMock(
            spec=create.CloudFrontDistributionStackCreator
        )
        MockModule.create_static_website.return_value = mock_object

        assert mock_object.deploy_static_site.call_count == 0

        Args.action = 'deploy'
        commands.main(Args)

        assert mock_object.deploy_static_site.call_count == 1
        mock_object.deploy_static_site.assert_called_once_with()
