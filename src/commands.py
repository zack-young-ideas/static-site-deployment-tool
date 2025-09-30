#!/usr/bin/env python3

from src import create, iam, validators


def main(args):
    arguments = validators.Arguments(
        args.action,
        args.domain
    )
    arguments.validate_arguments()
    if arguments.action == 'iam':
        iam.create_iam_template('define_iam_user.yml')
    elif arguments.action == 'deploy':
        create.create_static_website(arguments.domain_name)
