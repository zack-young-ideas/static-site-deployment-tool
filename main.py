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
    args = parser.parse_args()
    commands.main(args)
