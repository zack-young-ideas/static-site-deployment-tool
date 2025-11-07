from troposphere import Template

import definitions


def test_generates_proper_template():
    template = Template()
    definitions.CloudFormationTemplate(
        domain_name='example.com',
        template=template,
        homepage='index.html',
        _404_page='404.html',
        _500_page='500.html',
        hosted_zone='1234',
        certificate_arn='arn:aws:acm:us-east-1:1234:certificate/5678'
    )
    actual_content = template.to_yaml().splitlines(keepends=True)
    # Must delete line that contains random string.
    del actual_content[24]
    actual_content = ''.join(actual_content)

    with open('tests/expected_cloudfront_template.yml', 'r') as output_file:
        expected_content = output_file.readlines()
        # Must delete line that contains random string.
        del expected_content[24]
        expected_content = ''.join(expected_content)

    assert actual_content == expected_content
