#!/usr/bin/env python3

from src import iam, validators


def main(args):
    arguments = validators.Arguments(args.action)
    arguments.validate_arguments()
    if arguments.action == 'iam':
        iam.create_iam_template()
