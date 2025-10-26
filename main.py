#!/usr/bin/env python3
"""
Command-line tool used to deploy a static website to AWS.
"""

import argparse

from src import commands


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['iam', 'deploy'],
        help=(
            'Indicate which action to perform; choices are `iam` and `deploy`'
        )
    )
    parser.add_argument(
        'domain',
        nargs='?',
        default='',
        help='The domain name of the website'
    )
    parser.add_argument(
        'source_directory',
        nargs='?',
        default='',
        help='The directory that contains the website\'s static files'
    )
    args = parser.parse_args()
    commands.main(args)
