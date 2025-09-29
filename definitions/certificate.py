"""
Provisions an SSL certificate for the website using AWS Certificate
Manager.
"""

from troposphere import certificatemanager


class ACMCertificate:

    def define_ssl_certificate(self):
        self._acm_certificate = self.template.add_resource(
            certificatemanager.Certificate(
                self.names['acm_certificate'],
                DomainName=f'www.{self.domain_name}',
                DomainValidationOptions=[
                    certificatemanager.DomainValidationOption(
                        DomainName=f'www.{self.domain_name}',
                        HostedZoneId=self._hosted_zone_id
                    ),
                ],
                SubjectAlternativeNames=[self.domain_name],
                ValidationMethod='DNS'
            )
        )
