#!/usr/bin/env python3
"""
Command-line tool used to deploy a static website to AWS.
"""

import argparse

from src import main


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
        '--config',
        default='settings.py',
        help='The location of the file containing required settings'
    )
    args = parser.parse_args()
    main(args)
