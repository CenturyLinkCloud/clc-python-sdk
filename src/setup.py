#
# python setup.py sdist
# python setup.py bdist_dumb
# python setup.py bdist_rpm
#

# follow notes from https://packaging.python.org/distributing/#id69
# and release with `python setup.py sdist upload`
from __future__ import unicode_literals
from setuptools import setup, find_packages

setup(
	name = "clc-sdk",
	version = "2.51",
	packages = find_packages("."),

	install_requires = ['prettytable','clint','argparse','requests'],

	entry_points = {
		'console_scripts': [
			'clc  = clc.APIv1.cli:main',
		],
	},


	# metadata for upload to PyPI
	author = "CenturyLink Cloud",
	author_email = "ecosystem@centurylink.com",
	description = "CenturyLink Cloud SDK and CLI",
	keywords = "CenturyLink Cloud SDK CLI",
	url = "https://github.com/CenturyLinkCloud/clc-python-sdk",

	classifiers=[ # See https://pypi.org/pypi?%3Aaction=list_classifiers
		"Natural Language :: English",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",  # v2 API only
	],
)

