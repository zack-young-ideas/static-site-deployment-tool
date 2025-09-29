"""
Defines two DNS record sets that point to the website using AWS Route53.
"""

from troposphere import GetAtt, route53


class RecordSets:

    def define_record_sets(self):
        self.template.add_resource(route53.RecordSetGroup(
            'StaticSiteDomainRecordSet',
            HostedZoneName=f'{self.domain_name}.',
            RecordSets=[
                route53.RecordSet(
                    AliasTarget=route53.AliasTarget(
                        DNSName=GetAtt(
                            self.names['cloudfront_distribution'],
                            'DomainName'
                        ),
                        EvaluateTargetHealth=False,
                        HostedZoneId=self.hosted_zone
                    ),
                    Name=self.domain_name,
                    Type='A'
                )
            ]
        ))
        self.template.add_resource(route53.RecordSetGroup(
            'StaticSiteSubDomainRecordSet',
            HostedZoneName=f'{self.domain_name}.',
            RecordSets=[
                route53.RecordSet(
                    AliasTarget=route53.AliasTarget(
                        DNSName=GetAtt(
                            self.names['cloudfront_distribution'],
                            'DomainName'
                        ),
                        EvaluateTargetHealth=False,
                        HostedZoneId=self.hosted_zone
                    ),
                    Name=f'www.{self.domain_name}',
                    Type='A'
                )
            ]
        ))
