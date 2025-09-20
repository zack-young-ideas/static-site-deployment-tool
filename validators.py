class Arguments:

    def __init__(self, action=None):
        self.action = action

    def validate_arguments(self):
        if not self.action:
            raise Exception('Must provide `action` argument')
        if self.action not in ['iam', 'deploy']:
            raise Exception('Must provide `action` argument')
