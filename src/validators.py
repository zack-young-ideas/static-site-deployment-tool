"""
Defines classes used to validate command-line arguments.
"""

import abc
import importlib
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Validator(abc.ABC):

    def __init__(self, default_value=None):
        self._value = default_value

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._value

    def __set__(self, obj, value):
        self.validate(value)
        self._value = value

    @abc.abstractmethod
    def validate(self, value):
        pass


class String(Validator):

    def __init__(self, *options, default_value=None):
        Validator.__init__(self, default_value)
        self.options = set(options)

    def validate(self, value):
        # Value must be a string.
        if type(value) is not str:
            raise TypeError(f'{self.public_name} must be a valid string')

        # If no allowed strings are specified, then any string is valid.
        if len(self.options) == 0:
            return

        # If a list of allowed strings is given, the value must be in
        # that list.
        if value not in self.options:
            raise ValueError(
                f'{self.public_name} argument must be one of {self.options!r}'
            )


class Boolean(Validator):

    def validate(self, value):
        # Value must be a boolean.
        if value not in (True, False):
            raise TypeError(f'{self.public_name} must be either True or False')


class Arguments:
    """
    Validates settings and command-line arguments.
    """

    IAM_USER_TEMPLATE = String()
    TEMPLATE_FORMAT = String('JSON', 'YAML', default_value='YAML')
    SOURCE_FILES_DIRECTORY = String()
    DOMAIN_NAME = String()
    INDEX_FILE = String(default_value='index.html')
    _404_FILE = String(
        default_value=os.path.join(BASE_DIR, 'html', '404.html')
    )
    _500_FILE = String(
        default_value=os.path.join(BASE_DIR, 'html', '500.html')
    )
    REGISTER_DOMAIN = Boolean(default_value=True)
    HTML_EXTENSIONS = Boolean(default_value=True)

    def __init__(self, action=None, settings_file=None):
        self.action = action
        self.settings_file = settings_file
        self._validate_arguments()

    def _validate_arguments(self):
        """
        Ensures that arguments and settings are valid.
        """
        # Ensure that proper value is given for the action argument.
        if not self.action:
            raise ValueError('Must provide value for action argument')
        if self.action not in ['iam', 'deploy']:
            raise ValueError(
                "action setting must be either 'iam' or 'deploy'"
            )

        # Ensure that settings_file exists.
        if not os.path.isfile(self.settings_file):
            raise FileNotFoundError(
                f'File {self.settings_file} does not exist'
            )

        # Ensure that the settings defined in settings_file are valid.
        module_name = os.path.splitext(self.settings_file)[0]
        mod = importlib.import_module(module_name)
        for setting in dir(mod):
            setting_value = getattr(mod, setting)
            setattr(self, setting, setting_value)

        if self.action == 'deploy':
            required_settings = (
                'SOURCE_FILES_DIRECTORY',
                'DOMAIN_NAME',
            )
            # Ensure that required settings are assigned a value.
            for setting in required_settings:
                if not hasattr(mod, setting):
                    raise ValueError(
                        ''.join([
                            f'{setting} setting is required but not ',
                            'assigned a value',
                        ])
                    )
