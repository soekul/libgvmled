# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='libgvmled',
    version="1.0",
    description="Library for control of GVM Led Lamps",
    author="Luke Stamm",
    packages=find_packages(),
    include_package_data=False,
    install_requires=["binascii"],
)
