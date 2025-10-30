"""
Defines a class that produces a CF template to create a CloudFront
distribution.

The CloudFrontDistributionStackCreator class has methods that can
compose a CloudFormation template that defines the resources needed
to deploy a static website, create a new stack with that CF template,
and upload static files to an S3 bucket so that the site will be served
by a CloudFront distribution.
"""

import mimetypes
import os
import sys
import time

import boto3
from botocore.exceptions import ClientError

from troposphere import Template

import definitions
from src import utils


class CloudFrontDistributionStackCreator(utils.CloudFormationStackCreator):

    def __init__(self, arguments):
        self.domain_name = arguments.DOMAIN_NAME
        self.homepage = arguments.INDEX_FILE
        self.source_directory = arguments.SOURCE_FILES_DIRECTORY
        self.template = Template()
        self.hosted_zone = self.get_hosted_zone_id()

    def deploy_static_site(self):
        """
        Runs all the commands needed to create the site.
        """
        certificate_arn = self._create_certificate()
        validation_records = self._retrieve_validation_records(certificate_arn)
        self._create_CNAME_records(validation_records)
        self._check_certificate_status(certificate_arn)
        definitions.CloudFormationTemplate(
            domain_name=self.domain_name,
            template=self.template,
            homepage=self.homepage,
            hosted_zone=self.hosted_zone,
            certificate_arn=certificate_arn
        )
        self.create_stack(
            template=self.template,
            stack_name='static-website'
        )
        s3_bucket_name = self.get_s3_bucket_name()
        self._upload_files(s3_bucket_name=s3_bucket_name)

    def _create_certificate(self):
        """
        Creates an SSL certificate using AWS Certificate Manager.
        """
        print('Creating SSL certificate...')
        client = boto3.client('acm')
        try:
            response = client.request_certificate(
                DomainName=self.domain_name,
                SubjectAlternativeNames=[f'www.{self.domain_name}'],
                ValidationMethod='DNS'
            )
            certificate_arn = response['CertificateArn']
        except ClientError as err:
            print(f'Error requesting certificate: {err}')
            sys.exit(1)
        else:
            return certificate_arn

    def _retrieve_validation_records(self, certificate_arn):
        """
        Retrieves the certificate's validation records.
        """
        client = boto3.client('acm')
        validation_records = None
        max_retries = 10
        retries = 0
        while retries < max_retries:
            try:
                response = client.describe_certificate(
                    CertificateArn=certificate_arn
                )
                validation_options = (
                    response['Certificate']['DomainValidationOptions']
                )
                if (validation_options and
                        ('ResourceRecord' in validation_options[0])):
                    validation_records = [dvo['ResourceRecord'] for
                                          dvo in validation_options]
                    break
            except ClientError:
                pass
            print(''.join([
                'Validation records not available yet. Waiting 10 seconds. ',
                f'Retry {retries + 1}/{max_retries}'
            ]))
            time.sleep(10)
            retries += 1
        if not validation_records:
            print('Timed out waiting for validation records.')
            sys.exit(1)
        else:
            return validation_records

    def _create_CNAME_records(self, validation_records):
        """
        Creates CNAME records to validate SSL certificate.
        """
        client = boto3.client('route53')
        try:
            route53_changes = []
            for record in validation_records:
                route53_changes.append({
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record['Name'],
                        'Type': record['Type'],
                        'TTL': 300,
                        'ResourceRecords': [{
                            'Value': record['Value'],
                        }],
                    },
                })
            client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone,
                ChangeBatch={
                    'Comment': (
                        'Adding DNS validation records for SSL certificate'
                    ),
                    'Changes': route53_changes,
                },
            )
        except ClientError as err:
            print(f'Error creating Route53 record set: {err}')
            sys.exit(1)

    def _check_certificate_status(self, certificate_arn):
        client = boto3.client('acm')
        print('Certificate is pending validation...')
        while True:
            response = client.describe_certificate(
                CertificateArn=certificate_arn
            )
            status = response['Certificate']['Status']

            if status == 'ISSUED':
                print(''.join([
                    f'Certificate {certificate_arn} has been successfully ',
                    'validated and issued!'
                ]))
                return
            if status == 'FAILED':
                print(''.join([
                    'Certificate validation failed. Reason: ',
                    f"{response['Certificate']['FailureReason']}"
                ]))
                sys.exit(1)
            time.sleep(30)

    def _upload_files(self, s3_bucket_name):
        """
        Uploads the static site files to the S3 bucket.
        """
        print('Uploading static files to S3 bucket...')
        client = boto3.client('s3')
        for root, directory, files in os.walk(self.source_directory):
            for file in files:
                # Determine the location of the file on the local disk.
                local_filepath = os.path.join(root, file)

                # Determine the URL the file should have.
                parent_dir = root.split(self.source_directory)[-1:][0]
                if parent_dir:
                    file_url = (
                        '/'.join(parent_dir.split(os.sep)).lstrip('/')
                        + '/'
                        + file
                    )
                else:
                    file_url = file

                # Determine the MIME type of each file.
                mime_type, _ = mimetypes.guess_type(file)

                # Upload the file to the S3 bucket.
                client.upload_file(
                    local_filepath,
                    s3_bucket_name,
                    file_url,
                    {'ContentType': mime_type}
                )
        print('Finished')

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
