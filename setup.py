# setup.py

from setuptools import setup, find_packages

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='latexpages',
    version='0.2.2',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Combine LaTeX docs into a single PDF',
    keywords='pdfpages parallel compilation proceedings',
    license='MIT',
    url='http://github.com/xflr6/latexpages',
    packages=find_packages(),
    package_data={'latexpages': ['template.tex', 'settings.ini']},
    entry_points={'console_scripts': [
        'latexpages=latexpages:main',
        'latexpages-paginate=latexpages:main_paginate'
    ]},
    extras_require={
        'dev': ['wheel'],
        'test': ['nose', 'coverage', 'flake8', 'pep8-naming'],
    },
    platforms='any',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Printing',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
)
