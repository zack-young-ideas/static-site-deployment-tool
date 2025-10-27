from unittest.mock import patch

from src import create


class MockClient:
    """
    Mock boto3 Route53 client object used for testing.
    """
    @staticmethod
    def list_hosted_zones():
        return {
            'HostedZones': [{
                'Name': 'example.com',
                'Id': '/hostedzone/1234',
            }, {
                'Name': 'notreal.dev',
                'Id': '/hostedzone/5678',
            }, {
                'Name': 'otherwebsite.net',
                'Id': '/hostedzone/9022',
            }]
        }

    @staticmethod
    def upload_file():
        return None


@patch('src.create.boto3.client')
def test_can_retrieve_hosted_zone_id(mock_client):
    mock_client.return_value = MockClient

    instance = create.CloudFrontDistributionStackCreator(
        'example.com',
        './source_dir'
    )

    assert instance.get_hosted_zone_id() == '1234'


@patch('src.create.boto3.client')
def test_deploy_static_site_method_calls_create_stack_method(mock_client):
    mock_client.return_value = MockClient

    instance = create.CloudFrontDistributionStackCreator(
        'example.com',
        './source_dir'
    )

    with patch.object(instance, 'create_stack') as mock_create_stack_method:
        with patch.object(instance, 'get_s3_bucket_name'):
            assert mock_create_stack_method.call_count == 0

            instance.deploy_static_site()

            assert mock_create_stack_method.call_count == 1
            mock_create_stack_method.assert_called_once_with(
                template=instance.template,
                stack_name='static-website'
            )


@patch('src.create.boto3.client')
def test_deploy_static_site_method_calls_upload_files_method(mock_client):
    mock_client.return_value = MockClient

    instance = create.CloudFrontDistributionStackCreator(
        'example.com',
        './source_dir'
    )

    with patch.object(instance, '_upload_files') as mock_upload_files_method:
        with patch.object(instance, 'get_s3_bucket_name') as mock_s3_method:
            with patch.object(instance, 'create_stack'):
                mock_s3_method.return_value = 'StaticSiteS3Bucket'

                assert mock_upload_files_method.call_count == 0

                instance.deploy_static_site()

                assert mock_upload_files_method.call_count == 1
                mock_upload_files_method.assert_called_once_with(
                    s3_bucket_name='StaticSiteS3Bucket'
                )
