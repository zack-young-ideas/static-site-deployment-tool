from src import iam


def test_generates_random_password(tmp_path):
    file_path = tmp_path / 'output.yml'
    instance = iam.IAMTemplateGenerator(file_path, False)
    random_password = instance.generate_random_password()

    assert type(random_password) is str
    assert len(random_password) == 14


def test_writes_template_file(tmp_path):
    with open('tests/expected_iam_template.yml', 'r') as output_file:
        expected_content = output_file.readlines()
        # Must delete line that contains random password.
        del expected_content[12]
        expected_content = ''.join(expected_content)
    file_path = tmp_path / 'output.yml'
    iam.IAMTemplateGenerator(file_path, False)

    assert file_path.exists()

    with open(file_path) as f:
        actual_content = f.readlines()
        # Must delete line that contains random password.
        del actual_content[12]
        actual_content = ''.join(actual_content)

    assert actual_content == expected_content
