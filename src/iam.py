"""
Defines tools for creating CF templates that define IAM users.

The IAMTemplateGenerator class generates CloudFormation templates
that define an IAM user. This IAM user has the permissions
needed to provision all the resources that host the static site.
"""

import secrets
import string

from troposphere import GetAtt, iam, Output, Ref, Template


class IAMTemplateGenerator:

    def __init__(self, arguments):
        self._register_domain = arguments.REGISTER_DOMAIN
        self._filename_extension = arguments.TEMPLATE_FORMAT
        password = self.generate_random_password()
        print(f'IAM user password is {password}')
        template = self.generate_template(password)
        if self._filename_extension == 'JSON':
            extension = '.json'
        else:
            extension = '.yml'
        with open(f'{arguments.IAM_USER_TEMPLATE}{extension}', 'w') as the_juice:
            the_juice.write(template)

    def generate_random_password(self):
        """
        Generates a random password for the new user.
        """
        alphabet = string.ascii_uppercase + string.ascii_lowercase
        alphabet += string.digits + '!@#$%^&*?;:"{}/'
        return ''.join(secrets.choice(alphabet) for i in range(14))

    def generate_template(self, password):
        """
        Returns the CloudFormation template in the specified format.
        """
        template = Template()
        template.set_description(
            'AWS CloudFormation Template: This template creates a new IAM '
            + 'user and grants them the permissions needed to create a static '
            + 'website using S3 and CloudFront.'
        )
        self.add_resources(template=template, password=password)
        if self._filename_extension == 'JSON':
            return template.to_json()
        else:
            return template.to_yaml()

    def add_resources(self, template, password):
        """
        Defines the IAM user needed to create the static site.
        """
        iam_policy_document = self.generate_iam_policy_document()
        user = template.add_resource(
            iam.User(
                'StaticSiteAdmin',
                LoginProfile=iam.LoginProfile(
                    Password=password,
                    PasswordResetRequired=True
                ),
                UserName='static_site_admin'
            )
        )
        group = template.add_resource(
            iam.Group('StaticSiteAdminGroup')
        )
        access_key = template.add_resource(
            iam.AccessKey(
                'StaticSiteAdminKey',
                Status='Active',
                UserName=Ref(user)
            )
        )
        template.add_resource(
            iam.UserToGroupAddition(
                'StaticSiteAdminGroupUser',
                GroupName=Ref(group),
                Users=[Ref(user)]
            )
        )
        template.add_resource(
            iam.PolicyType(
                'StaticSiteAdminGroupPolicy',
                PolicyName='StaticSiteAdmin',
                Groups=[Ref(group)],
                PolicyDocument=iam_policy_document
            )
        )
        template.add_output(
            Output(
                'AccessKey',
                Value=Ref(access_key),
                Description='AWS access key ID for static site admin user'
            )
        )
        template.add_output(
            Output(
                'SecretKey',
                Value=GetAtt(access_key, 'SecretAccessKey'),
                Description='AWS secret access key for static site admin user'
            )
        )

    def generate_iam_policy_document(self):
        """
        Returns policy document that defines IAM user's permissions.
        """
        statement = [{
            'Sid': 'AllowS3BucketCreationPermissions',
            'Effect': 'Allow',
            'Action': [
                's3:CreateBucket',
                's3:GetBucketPolicy',
                's3:GetBucketLocation',
                's3:GetObject',
                's3:ListAllMyBuckets',
                's3:ListBucket',
                's3:PutBucketPolicy',
                's3:PutEncryptionConfiguration',
                's3:PutObject',
                's3:TagResource',
            ],
            'Resource': '*'
        }, {
            'Sid': 'AllowACMCertificateRequestPermissions',
            'Effect': 'Allow',
            'Action': [
                'acm:AddTagsToCertificate',
                'acm:DescribeCertificate',
                'acm:GetCertificate',
                'acm:ImportCertificate',
                'acm:ListCertificates',
                'acm:ListTagsForCertificate',
                'acm:RequestCertificate',
            ],
            'Resource': '*'
        }, {
            'Sid': 'AllowRecordSetGroupCreationPermissions',
            'Effect': 'Allow',
            'Action': [
                'route53:ChangeResourceRecordSets',
                'route53:ChangeTagsForResource',
                'route53:GetChange',
                'route53:GetHostedZone',
                'route53:ListHostedZones',
            ],
            'Resource': '*'
        }, {
            'Sid': 'AllowCloudFrontCachePolicyCreationPermissions',
            'Effect': 'Allow',
            'Action': [
                'cloudfront:CreateCachePolicy',
                'cloudfront:CreateDistribution',
                'cloudfront:CreateOriginAccessControl',
                'cloudfront:CreateResponseHeadersPolicy',
                'cloudfront:GetCachePolicy',
                'cloudfront:GetDistribution',
                'cloudfront:GetDistributionConfig',
                'cloudfront:GetOriginAccessControl',
                'cloudfront:GetResponseHeadersPolicyConfig',
                'cloudfront:GetResponseHeadersPolicy',
                'cloudfront:ListCachePolicies',
                'cloudfront:ListDistributions',
                'cloudfront:TagResource',
                'cloudfront:UpdateDistribution',
                'cloudfront:UpdateOriginAccessControl',
            ],
            'Resource': '*'
        }, {
            'Sid': 'AllowCloudFormationStackCreationPermissions',
            'Effect': 'Allow',
            'Action': [
                'cloudformation:CreateStack',
                'cloudformation:DescribeStacks',
            ],
            'Resource': '*'
        }]
        if self._register_domain:
            statement.append({
                'Sid': 'AllowDomainNamePermissions',
                'Effect': 'Allow',
                'Action': [
                    'route53domains:CheckDomainAvailability',
                    'route53domains:CheckDomainTransferability',
                    'route53domains:GetDomainDetail',
                    'route53domains:ListDomains',
                    'route53domains:ListOperations',
                    'route53domains:ListPrices',
                    'route53domains:RegisterDomain',
                    'route53domains:TransferDomain',
                    'route53domains:RetrieveDomainAuthCode',
                    'route53domains:UpdateDomainContact',
                    'route53domains:UpdateDomainContactPrivacy',
                    'route53domains:UpdateDomainNameservers',
                ],
                'Resource': '*'
            })
        policy_document = {
            'Version': '2012-10-17',
            'Statement': statement
        }
        return policy_document


create_iam_template = IAMTemplateGenerator
