"""
Defines a class used to validate command-line arguments.
"""


class Arguments:

    def __init__(
            self, action=None,(
            domain_support=None,
            domain_name=None,
            source_dir=None
    ):
        self.action = action
        self.domain_support = domain_support
        self.domain_name = domain_name
        self.source_dir = source_dir

    def validate_arguments(self):
        if not self.action:
            raise Exception('Must provide `action` argument')
        if self.action not in ['iam', 'deploy']:
            raise Exception(
                '`action` argument must be either `iam` or `deploy`'
            )
        if self.action == 'deploy':
            if not self.domain_name:
                raise Exception(
                    'Must provide a domain name for website deployment'
                )
            if not self.source_dir:
                raise Exception(
                    'Must provide a directory containing website static files'
                )
        if (self.domain_support and (self.action != 'iam')):
            raise Exception(
                ''.join([
                    'Argument --domain-support is invalid when used with ',
                    'iam command'
                ])
            )
