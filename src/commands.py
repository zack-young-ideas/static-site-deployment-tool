#!/usr/bin/env python3

from src import create, iam, validators


def main(args):
    arguments = validators.Arguments(
        args.action,
        args.domain,
        args.source_directory
    )
    arguments.validate_arguments()
    if arguments.action == 'iam':
        iam.create_iam_template('define_iam_user.yml')
    elif arguments.action == 'deploy':
        create_object = create.create_static_website(
            arguments.domain_name,
            arguments.source_dir
        )
        create_object.deploy_static_site()
