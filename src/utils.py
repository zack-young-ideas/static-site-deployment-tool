"""
Defines a utility class for creating CloudFormation stacks.
"""

import sys
import time

import boto3


class CloudFormationStackCreator:

    _client = boto3.client('cloudformation')

    def create_stack(self, template, stack_name):
        """
        Creates a new stack and waits for CREATE_COMPLETE status.
        """
        self._client.create_stack(
            StackName=stack_name,
            TemplateBody=template.to_yaml(),
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure='DELETE'
        )
        print(f"Creating CloudFormation stack '{stack_name}'... ", end='')
        status = self._check_stack_creation_status(stack_name)
        if status:
            print('Stack created successfully')
        else:
            raise SystemExit('Stack creation failed')

    def _check_stack_creation_status(self, stack_name):
        """
        Displays loading spinner while stack is being created.
        """
        spinner = self._spinning_cursor()
        response = self._client.describe_stacks(
            StackName=stack_name
        )
        stack, stack_index = self._find_stack_in_response(response, stack_name)
        stack_status = stack['StackStatus']
        while stack_status == 'CREATE_IN_PROGRESS':
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
            response = self._client.describe_stacks(
                StackName=stack_name
            )
            stack = response['Stacks'][stack_index]
            stack_status = stack['StackStatus']
        sys.stdout.write('\n')
        if stack_status == 'CREATE_COMPLETE':
            return True
        else:
            return False

    def _spinning_cursor(self):
        """
        Generator function used to display loading spinner.
        """
        while True:
            for cursor in '|/-\\':
                yield cursor

    def _get_stack_output(self, stack_name, key_name):
        """
        Returns the output of the stack.
        """
        response = self._client.describe_stacks(
            StackName=stack_name
        )
        stack = self._find_stack_in_response(response, stack_name)[0]
        output_index = 0
        output = stack['Outputs'][output_index]
        while output['OutputKey'] != key_name:
            output_index += 1
            try:
                output = stack['Outputs'][output_index]
            except IndexError:
                raise SystemExit(f"Output '{key_name}' could not be found")
        return output['OutputValue']

    def _find_stack_in_response(self, response, stack_name):
        """
        Finds the desired stack info in the JSON response.
        """
        stack_index = 0
        stack = response['Stacks'][stack_index]
        while stack['StackName'] != stack_name:
            stack_index += 1
            try:
                stack = response['Stacks'][stack_index]
            except IndexError:
                raise SystemExit(f"Stack '{stack_name}' could not be found")
        return (stack, stack_index)
