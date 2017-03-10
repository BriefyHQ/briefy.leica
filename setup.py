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
    'apscheduler',
    'boto3',
    'briefy.common',
    'briefy.ws',
    'colanderalchemy',
    'cornice==2.2.0',
    'newrelic',
    'phonenumbers',
    'pycountry',
    'pyramid==1.7.3',
    'pyramid_tm',
    'pyramid_zcml',
    'requests',
    'setuptools',
    's3transfer==0.1.10',
    'sqlalchemy',
    'sqlalchemy_continuum',
    'waitress',
    'wheel',
    'workdays',
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
    version='2.0.27',
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
    [paste.app_factory]
     main = briefy.leica:main
    [console_scripts]
     worker = briefy.leica.worker:main
     leica_tasks = briefy.leica.tasks:main
    """,
)
