"""
Defines a class that produces a CF template to create a CloudFront
distribution.

The CloudFrontDistributionStackCreator class has methods that can
compose a CloudFormation template that defines the resources needed
to deploy a static website, create a new stack with that CF template,
and upload static files to an S3 bucket so that the site will be served
by a CloudFront distribution.
"""

import boto3

from troposphere import Template

import definitions


class CloudFrontDistributionStackCreator:

    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.template = Template()
        self.hosted_zone = self.get_hosted_zone_id()

    def deploy_static_site(self):
        """
        Runs all the commands needed to create the site.
        """
        definitions.CloudFormationTemplate(
            domain_name=self.domain_name,
            template=self.template,
            hosted_zone=self.hosted_zone
        )

    def get_hosted_zone_id(self):
        """
        Retrieves the hosted zone ID for the site's domain name.

        Note: Assumes a hosted zone already exists for the specified
        domain.
        """
        client = boto3.client('route53')
        hosted_zones = client.list_hosted_zones()
        print(hosted_zones)
        hosted_zone_id = None
        for item in hosted_zones['HostedZones']:
            if item['Name'] in [self.domain_name, f'{self.domain_name}.']:
                hosted_zone_id = item['Id'].split('/')[2]
        if hosted_zone_id:
            return hosted_zone_id
        else:
            error_message = (
                'Could not find hosted zone for domain name '
                + f"'{self.domain_name}'"
            )
            raise Exception(error_message)


create_static_website = CloudFrontDistributionStackCreator
