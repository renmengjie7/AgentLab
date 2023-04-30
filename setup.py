#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="AISimuToolKit",  # package name
    version="0.1.4",  # version
    keywords=["pip", "AISimuToolKit"],  # keywords
    description="ICIP's private utils.",  # description
    long_description="ICIP's private utils. The development version will be released when it is sufficiently refined",
    license="Apache License 2.0",
    url="http://git.cipsup.cn/aisimulationplatform/toolkit/aisimulation",  # github
    author="Ren & Guo", 
    author_email="renmengjie22@mails.ucas.ac.cn,guoshiguang22@mails.ucas.edu.cn",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    python_requires='>=3.10',
    install_requires=["openai==0.27.4", "pandas==1.5.3", "PyYAML==6.0", "Requests==2.28.2", "scikit_learn==1.2.2", "setuptools==65.6.3", "torch==1.13.1", "transformers==4.24.0"]
)
