"""
Example configuration file.
"""

# The name of the CF template that creates a new IAM user.
IAM_USER_TEMPLATE = 'create_iam_template'
# The TEMPLATE_FORMAT variable indicates whether the CF
# template should be in JSON or YAML.
TEMPLATE_FORMAT = 'YAML'

# The directory that contains the site's static files.
SOURCE_FILES_DIRECTORY = 'source_dir'

# The domain name for the site.
DOMAIN_NAME = 'example.com'

# The homepage of the site.
INDEX_FILE = 'index.html'
# The default 404 and 500 error pages.
_404_FILE = '404.html'
_500_FILE = '500.html'

# If REGISTER_DOMAIN is set to True, the IAM user will have the
# permissions needed to purchase and register a new domain name.
REGISTER_DOMAIN = False

# If HTML_EXTENSIONS is set to False, the .html extension will
# be removed from every file; this makes the URLs of the site
# more aesthetic (i.e., /about instead of /about.html).
HTML_EXTENSIONS = False
