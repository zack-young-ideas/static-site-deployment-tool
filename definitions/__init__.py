"""
Defines a class that represents the CloudFormation template.
"""

from . import cf_distribution, record_sets, s3_bucket


class CloudFormationTemplate(
    cf_distribution.CloudFrontDistribution,
    record_sets.RecordSets,
    s3_bucket.S3Bucket
):

    def __init__(self, domain_name, template, homepage,
                 _404_page, _500_page, hosted_zone, certificate_arn):
        self.domain_name = domain_name
        self.template = template
        self.homepage = homepage
        self._404_page = _404_page
        self._500_page = _500_page
        # Hosted zone ID.
        self.hosted_zone = hosted_zone
        # The ARN of the SSL certificate.
        self.certificate_arn = certificate_arn
        # Names that are referenced by multiple template resources.
        self.names = {
            'cloudfront_distribution': 'StaticSiteCloudFrontDistribution',
            's3_bucket': 'StaticWebsiteBucket',
        }

        self.define_record_sets()
        self.define_s3_bucket()
        self.define_cloudfront_distribution(
            self.homepage,
            self._404_page,
            self._500_page
        )
