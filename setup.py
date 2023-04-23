#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "AISimuToolKit",      #这里是pip项目发布的名称
    version = "0.0.5",  #版本号，数值大的会优先被pip
    keywords = ["pip", "AISimuToolKit"],			# 关键字
    description = "ICIP's private utils.",	# 描述
    long_description = "ICIP's private utils. The development version will be released when it is sufficiently refined",
    license = "MIT Licence",		# 许可证
    url = "http://git.cipsup.cn/aisimulationplatform/toolkit/aisimulation",     #项目相关文件地址，一般是github项目地址即可
    author = "Ren & Guo",			# 作者
    author_email = "renmengjie22@mails.ucas.ac.cn",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    python_requires='>=3.10',
    install_requires = ["openai==0.27.4", "Requests==2.28.2", "pyyaml==6.0"]   #这个项目依赖的第三方库
)
