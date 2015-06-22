# coding: utf-8

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-upwork-auth',
    version='1.0-dev',
    packages=['django_upwork_auth'],
    include_package_data=True,
    license='BSD License',
    description='Upwork OAuth login for your Django-based project',
    long_description=README,
    author='Upwork',
    author_email='python@upwork.com',
    maintainer='Anton Strogonoff',
    maintainer_email='anton@strogonoff.name',
    download_url='http://github.com/strogonoff/django-upwork-auth',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
