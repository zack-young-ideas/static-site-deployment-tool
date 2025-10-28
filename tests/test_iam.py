from src import iam


class MockArguments:
    """
    Mocks the Arguments object passed to IAMTemplateGenerator.
    """
    REGISTER_DOMAIN = False
    TEMPLATE_FORMAT = 'YAML'


def test_generates_random_password(tmp_path):
    MockArguments.IAM_USER_TEMPLATE = tmp_path / 'output'
    instance = iam.IAMTemplateGenerator(MockArguments)
    random_password = instance.generate_random_password()

    assert type(random_password) is str
    assert len(random_password) == 14


def test_writes_template_file(tmp_path):
    with open('tests/expected_iam_template.yml', 'r') as output_file:
        expected_content = output_file.readlines()
        # Must delete line that contains random password.
        del expected_content[12]
        expected_content = ''.join(expected_content)
    MockArguments.IAM_USER_TEMPLATE = tmp_path / 'output'
    iam.IAMTemplateGenerator(MockArguments)
    output_file = tmp_path / 'output.yml'

    assert output_file.exists()

    with open(output_file) as f:
        actual_content = f.readlines()
        # Must delete line that contains random password.
        del actual_content[12]
        actual_content = ''.join(actual_content)

    assert actual_content == expected_content
