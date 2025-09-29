"""
Defines an S3 bucket that will store the static files of the website.
"""

from troposphere import s3


class S3Bucket:

    def define_s3_bucket(self):
        s3_bucket = self.template.add_resource(s3.Bucket(
            self.names['s3_bucket'],
            BucketEncryption=s3.BucketEncryption(
                ServerSideEncryptionConfiguration=[
                    s3.ServerSideEncryptionRule(
                        ServerSideEncryptionByDefault=(
                            s3.ServerSideEncryptionByDefault(
                                SSEAlgorithm='AES256'
                            )
                        )
                    )
                ]
            )
        ))
        # The S3 bucket name must be retrieved so that the static files
        # can be uploaded to the bucket later.
        self.template.add_output(Output(
            'S3BucketName',
            Value=Ref(s3_bucket),
            Description='Name of the S3 bucket that holds static files'
        ))
