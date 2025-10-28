"""
Defines a function that is called by the main.py file.
"""

from src import validators, create, iam


def main(argparse_arguments):
    """
    Can create a CF template defining a new IAM user or deploy a static site.
    """
    arguments = validators.Arguments(
        argparse_arguments.action,
        argparse_arguments.config
    )

    if arguments.action == 'iam':
        # Create a CloudFormation template that defines an IAM user
        # with the permissions needed to deploy a static website to AWS.
        iam.create_iam_template(arguments)
    else:
        # Provision the resources needed to deploy a static website to
        # AWS and then upload the static files to an S3 bucket.
        create_object = create.create_static_website(arguments)
        create_object.deploy_static_site()
