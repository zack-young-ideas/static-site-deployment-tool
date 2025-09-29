"""
Defines a CloudFront distribution to serve the website's static files.
"""

import random

from troposphere import cloudfront, GetAtt, Ref, s3, Sub


class CloudFrontDistribution:

    @property
    def random_string(self):
        """
        Generates a random string to use when naming the origin access
        control policy.
        """
        random_string = ''
        while len(random_string) < 20:
            random_string += str(random.randint(0, 10))
        return random_string

    def define_cloudfront_distribution(self):
        self.template.add_resource(s3.BucketPolicy(
            'StaticWebsiteBucketPolicy',
            Bucket=Ref(self.names['s3_bucket']),
            PolicyDocument={
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': 's3:GetObject',
                        'Condition': {
                            'StringEquals': {
                                'AWS:SourceArn': Sub(
                                    'arn:aws:cloudfront::${AWS::AccountId}'
                                    ':distribution/'
                                    '${CloudFrontDistribution}'
                                )
                            }
                        },
                        'Principal': {
                            'Service': ['cloudfront.amazonaws.com']
                        },
                        'Resource': Sub(
                            '${S3BucketArn}/*',
                            {'S3BucketArn': GetAtt(
                                self.names['s3_bucket'],
                                'Arn'
                            )}
                        )
                    },
                    {
                        'Effect': 'Allow',
                        'Action': 's3:ListBucket',
                        'Condition': {
                            'StringEquals': {
                                'AWS:SourceArn': Sub(
                                    'arn:aws:cloudfront::${AWS::AccountId}'
                                    ':distribution/'
                                    '${CloudFrontDistribution}'
                                )
                            }
                        },
                        'Principal': {
                            'Service': ['cloudfront.amazonaws.com']
                        },
                        'Resource': GetAtt(self.names['s3_bucket'], 'Arn'),
                    }
                ]
            }
        ))
        cache_policy = self.template.add_resource(cloudfront.CachePolicy(
            'CloudFrontCachePolicy',
            CachePolicyConfig=cloudfront.CachePolicyConfig(
                DefaultTTL=86400,
                MaxTTL=31536000,
                MinTTL=0,
                Name=Sub('${AWS::StackName}-static-site-cache-policy'),
                ParametersInCacheKeyAndForwardedToOrigin=(
                    cloudfront.ParametersInCacheKeyAndForwardedToOrigin(
                        CookiesConfig=cloudfront.CacheCookiesConfig(
                            CookieBehavior='none'
                        ),
                        EnableAcceptEncodingGzip=True,
                        HeadersConfig=cloudfront.CacheHeadersConfig(
                            HeaderBehavior='none'
                        ),
                        QueryStringsConfig=(
                            cloudfront.CacheQueryStringsConfig(
                                QueryStringBehavior='all'
                            )
                        )
                    )
                )
            )
        ))
        response_headers_policy = self.template.add_resource(
            cloudfront.ResponseHeadersPolicy(
                'CloudFrontResponseHeadersPolicy',
                ResponseHeadersPolicyConfig=(
                    cloudfront.ResponseHeadersPolicyConfig(
                        Name=Sub(
                            '${AWS::StackName}-static-site-security-headers'
                        ),
                        SecurityHeadersConfig=cloudfront.SecurityHeadersConfig(
                            ContentSecurityPolicy=(
                                cloudfront.ContentSecurityPolicy(
                                    ContentSecurityPolicy=(
                                        "default-src 'none'; img-src 'self';"
                                        "script-src 'self'; style-src 'self';"
                                        "object-src 'none'"
                                    ),
                                    Override=True
                                )
                            ),
                            ContentTypeOptions=cloudfront.ContentTypeOptions(
                                Override=True
                            ),
                            FrameOptions=cloudfront.FrameOptions(
                                FrameOption='DENY',
                                Override=True
                            ),
                            ReferrerPolicy=cloudfront.ReferrerPolicy(
                                ReferrerPolicy='same-origin',
                                Override=True
                            ),
                            StrictTransportSecurity=(
                                cloudfront.StrictTransportSecurity(
                                    AccessControlMaxAgeSec=63072000,
                                    IncludeSubdomains=True,
                                    Override=True,
                                    Preload=True
                                )
                            ),
                            XSSProtection=cloudfront.XSSProtection(
                                ModeBlock=True,
                                Override=True,
                                Protection=True
                            )
                        )
                    )
                )
            )
        )
        origin_access_control_policy = self.template.add_resource(
            cloudfront.OriginAccessControl(
                'CloudFrontOriginAccessControlPolicy',
                OriginAccessControlConfig=cloudfront.OriginAccessControlConfig(
                    Name=f'secure-static-site-{self.random_string}',
                    OriginAccessControlOriginType='s3',
                    SigningBehavior='always',
                    SigningProtocol='sigv4'
                )
            )
        )
        self.template.add_resource(cloudfront.Distribution(
            self.names['cloudfront_distribution'],
            DistributionConfig=cloudfront.DistributionConfig(
                Aliases=[
                    self.domain_name,
                    f'www.{self.domain_name}'
                ],
                CustomErrorResponses=[
                    cloudfront.CustomErrorResponse(
                        ErrorCode=404,
                        ResponseCode=404,
                        ResponsePagePath='/404.html'
                    ),
                    cloudfront.CustomErrorResponse(
                        ErrorCode=500,
                        ResponseCode=500,
                        ResponsePagePath='/500.html'
                    ),
                ],
                DefaultCacheBehavior=cloudfront.DefaultCacheBehavior(
                    CachePolicyId=Ref(cache_policy),
                    Compress=True,
                    TargetOriginId=Sub('S3-${AWS::StackName}-root'),
                    ViewerProtocolPolicy='redirect-to-https',
                    ResponseHeadersPolicyId=Ref(response_headers_policy)
                ),
                DefaultRootObject='index.html',
                Enabled=True,
                HttpVersion='http2',
                IPV6Enabled=True,
                Origins=[
                    cloudfront.Origin(
                        DomainName=GetAtt(
                            self.names['s3_bucket'],
                            'DomainName'
                        ),
                        Id=Sub('S3-${AWS::StackName}-root'),
                        OriginAccessControlId=Ref(
                            origin_access_control_policy
                        ),
                        S3OriginConfig=cloudfront.S3OriginConfig()
                    )
                ],
                ViewerCertificate=cloudfront.ViewerCertificate(
                    AcmCertificateArn=Ref(self.names['acm_certificate']),
                    MinimumProtocolVersion='TLSv1.1_2016',
                    SslSupportMethod='sni-only'
                )
            )
        ))
