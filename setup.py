"""Image Handling System."""
from setuptools import find_packages
from setuptools import setup

import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'HISTORY.rst')) as f:
    CHANGES = f.read()

requires = [
    'briefy.common',
    'boto3',
    'newrelic',
    'requests',
    'setuptools',
    'wheel',
    'zope.component',
    'zope.configuration',
    'zope.event',
    'zope.interface',
]

test_requirements = [
    'flake8',
    'pytest'
]

setup(
    name='briefy.leica',
    version='0.1.0',
    description='Image Handling System',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Briefy Tech Team',
    author_email='developers@briefy.co',
    url='https://github.com/BriefyHQ/briefy.leica',
    keywords='briefy',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['briefy', ],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    tests_require=test_requirements,
    install_requires=requires,
    entry_points="""

    """,
)
