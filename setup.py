"""
Setup file to install dat-core as a library.
"""
import os
from setuptools import setup

project_path = os.path.dirname(os.path.abspath(__file__))

setup(
    name='dat-core',
    packages=['src'],
    # package_dir={'dat_core': 'src'},
    version='0.1',
    description=('Core library for Data Activation Tool'),
    url='https://datachannel.co/',
    license='MIT',
    zip_safe=False,
    install_requires=[],
)