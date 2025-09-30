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


@patch('src.create.boto3.client')
def test_can_retrieve_hosted_zone_id(mock_client):
    mock_client.return_value = MockClient

    instance = create.CloudFrontDistributionStackCreator('example.com')

    assert instance.get_hosted_zone_id() == '1234'
