import pytest

from src import create


# Return value of boto3.client('route53').list_hosted_zones().
hosted_zones = {
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


# Return value of boto3.client('acm').describe_certificate().
certificate_details = {
    'Certificate': {
        'DomainValidationOptions': [{
            'ResourceRecord': {
                'Name': '_randomString',
                'Type': 'CNAME',
                'Value': '_moreRandomness',
            }
        }, {
            'ResourceRecord': {
                'Name': '_yetAnotherRandomString',
                'Type': 'CNAME',
                'Value': '_evenMoreRandomness',
            }
        }],
        'Status': 'ISSUED',
    }
}


class MockArguments:
    """
    Mocks the Arguments object passed to
    CloudFrontDistributionStackCreator.
    """
    DOMAIN_NAME = 'example.com'
    INDEX_FILE = 'index.html'
    SOURCE_FILES_DIRECTORY = 'source_dir'


@pytest.fixture(autouse=True)
def mock_boto3_client(mocker):
    mock_boto3_client = mocker.patch('src.create.boto3.client')
    mock_acm = mocker.Mock()
    mock_acm.request_certificate.return_value = {
        'CertificateArn': 'arn:aws:acm:us-east-1:1234:certificate/5678'
    }
    mock_acm.describe_certificate.return_value = certificate_details
    mock_route53 = mocker.Mock()
    mock_route53.list_hosted_zones.return_value = hosted_zones
    mock_s3 = mocker.Mock()
    mock_boto3_client.side_effect = lambda service: {
        'acm': mock_acm,
        'route53': mock_route53,
        's3': mock_s3
    }[service]
    return {
        'acm': mock_acm,
        'client': mock_boto3_client,
        'route53': mock_route53,
        's3': mock_s3
    }


@pytest.fixture(autouse=True)
def mock_instance(mocker):
    instance = create.CloudFrontDistributionStackCreator(MockArguments)
    mock_create_stack = mocker.patch.object(instance, 'create_stack')
    mock_s3_bucket_name = mocker.patch.object(instance, 'get_s3_bucket_name')
    mock_s3_bucket_name.return_value = 'StaticSiteS3Bucket'
    mock_upload_files = mocker.patch.object(instance, '_upload_files')
    return {
        'instance': instance,
        'create_stack': mock_create_stack,
        'upload_files': mock_upload_files
    }


def test_can_retrieve_hosted_zone_id(mock_boto3_client, mock_instance):
    assert mock_instance['instance'].get_hosted_zone_id() == '1234'


def test_deploy_static_site_method_calls_create_stack_method(
    mock_boto3_client,
    mock_instance
):
    assert mock_instance['create_stack'].call_count == 0

    mock_instance['instance'].deploy_static_site()

    assert mock_instance['create_stack'].call_count == 1
    mock_instance['create_stack'].assert_called_once_with(
        template=mock_instance['instance'].template,
        stack_name='static-website'
    )


def test_deploy_static_site_method_calls_upload_file_method(
    mock_boto3_client,
    mock_instance
):
    assert mock_instance['upload_files'].call_count == 0

    mock_instance['instance'].deploy_static_site()

    assert mock_instance['upload_files'].call_count == 1
    mock_instance['upload_files'].assert_called_once_with(
        s3_bucket_name='StaticSiteS3Bucket'
    )
