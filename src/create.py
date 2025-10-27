"""
Defines a class that produces a CF template to create a CloudFront
distribution.

The CloudFrontDistributionStackCreator class has methods that can
compose a CloudFormation template that defines the resources needed
to deploy a static website, create a new stack with that CF template,
and upload static files to an S3 bucket so that the site will be served
by a CloudFront distribution.
"""

import os

import boto3

from troposphere import Template

import definitions
from src import utils


class CloudFrontDistributionStackCreator(utils.CloudFormationStackCreator):

    def __init__(self, domain_name, source_directory):
        self.domain_name = domain_name
        self.source_directory = source_directory
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
        self.create_stack(
            template=self.template,
            stack_name='static-website'
        )
        s3_bucket_name = self.get_s3_bucket_name()
        self._upload_files(s3_bucket_name=s3_bucket_name)

    def _upload_files(self, s3_bucket_name):
        """
        Uploads the static site files to the S3 bucket.
        """
        client = boto3.client('s3')
        for root, directory, files in os.walk(self.source_directory):
            for file in files:
                filename_prefix = root.split(os.sep)[3:]
                if filename_prefix:
                    fully_qualified_filename = os.path.join(
                        os.path.join(*filename_prefix),
                        file
                    )
                else:
                    fully_qualified_filename = file
                extension = os.path.splitext(file)[1]
                content_type = 'text/html'
                if extension == '.js':
                    content_type = 'text/javascript'
                if extension == '.css':
                    content_type = 'text/css'
                client.upload_file(
                    os.path.join(root, file),
                    s3_bucket_name,
                    fully_qualified_filename,
                    {'ContentType': content_type}
                )

    def get_hosted_zone_id(self):
        """
        Retrieves the hosted zone ID for the site's domain name.

        Note: Assumes a hosted zone already exists for the specified
        domain.
        """
        client = boto3.client('route53')
        hosted_zones = client.list_hosted_zones()
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

    def get_s3_bucket_name(self):
        """
        Retrieves the name of the S3 bucket.
        """
        return self._get_stack_output('static-website', 'S3BucketName')


create_static_website = CloudFrontDistributionStackCreator
