#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/2 0002 17:21
# @Author  : Hadrianl 
# @File    : setup.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as rm:
    long_description = rm.read()

setup(name='pyctp',
      version='1.0',
      description='CTP for python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Hadrianl',
      author_email='137150224@qq.com',
      url='https://github.com/hadrianl/huobi',
      packages=find_packages(),
      include_package_data = True,
      zip_safe=False,
      classifiers=("Programming Language :: Python :: 3.6",
                   "License :: OSI Approved :: MIT License"))