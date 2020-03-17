# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='flipdot',
    version='0.2.0',
    description='Driver and Simulator for Alfa-Zeta Flip-Dot',
    long_description=readme,
    author='J Whittington',
    author_email='git@jbrengineering.co.uk',
    url='https://github.com/tuna-f1sh/flipdot',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'Pillow',
        'pyserial',
    ],
)
