"""
Setup file to install dat-core as a library.
"""
import os
from setuptools import setup, find_packages

project_path = os.path.dirname(os.path.abspath(__file__))

setup(
    name='dat-core',
    version='0.1',
    description=('Core library for Data Activation Tool'),
    url='https://datachannel.co/',
    license='MIT',
    packages=find_packages(where=project_path),
    zip_safe=False,
    install_requires=[],
)