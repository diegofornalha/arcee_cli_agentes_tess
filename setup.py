#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re

# Ler a versão do arquivo __init__.py
with open(os.path.join('src', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = '0.1.0'  # Versão padrão se não conseguir encontrar

# Ler requisitos do arquivo requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='arcee-cli',
    version=version,
    description='CLI para interação com a API TESS através do MCP',
    author='TESS Team',
    author_email='info@pareto.io',
    url='https://github.com/fornalha/arcee-cli',
    packages=find_packages(),  # Alterado para encontrar todos os pacotes
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'arcee=src.__main__:cli',  # Mantendo o entry point original
            'arcee-cli=src.__main__:cli',  # Adicionando um entry point alternativo
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
) 