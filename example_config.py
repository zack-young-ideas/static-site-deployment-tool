"""
Example configuration file.
"""

# The name of the CF template that creates a new IAM user.
IAM_USER_TEMPLATE = 'create_iam_template'
# The TEMPLATE_FORMAT variable indicates whether the CF
# template should be in JSON or YAML; default is YAML.
TEMPLATE_FORMAT = 'YAML'

# The directory that contains the site's static files.
SOURCE_FILES_DIRECTORY = 'source_dir'

# The domain name for the site.
DOMAIN_NAME = 'example.com'

# The homepage of the site; defaults to index.html.
INDEX_FILE = 'index.html'
# The default 404 and 500 error pages.
_404_FILE = '404.html'
_500_FILE = '500.html'

# If REGISTER_DOMAIN is set to True, the IAM user will have the
# permissions needed to purchase and register a new domain name.
REGISTER_DOMAIN = False
