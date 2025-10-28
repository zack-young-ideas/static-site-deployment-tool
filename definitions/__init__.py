"""
Defines a class that represents the CloudFormation template.
"""

from . import certificate, cf_distribution, record_sets, s3_bucket


class CloudFormationTemplate(
    certificate.ACMCertificate,
    cf_distribution.CloudFrontDistribution,
    record_sets.RecordSets,
    s3_bucket.S3Bucket
):

    def __init__(self, domain_name, template, homepage, hosted_zone):
        self.domain_name = domain_name
        self.template = template
        self.homepage = homepage
        # Hosted zone ID.
        self.hosted_zone = hosted_zone

        # Names that are referenced by multiple template resources.
        self.names = {
            'acm_certificate': 'StaticSiteSSLCertificate',
            'cloudfront_distribution': 'StaticSiteCloudFrontDistribution',
            's3_bucket': 'StaticWebsiteBucket',
        }
        self.define_ssl_certificate()
        self.define_record_sets()
        self.define_s3_bucket()
        self.define_cloudfront_distribution(self.homepage)
