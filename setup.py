import pathlib
from setuptools import setup, find_packages

setup(
    name='latexpages',
    version='0.7.3.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Combine LaTeX docs into a single PDF',
    keywords='pdfpages parallel compilation proceedings',
    license='MIT',
    url='https://github.com/xflr6/latexpages',
    project_urls={
        'Issue Tracker': 'https://github.com/xflr6/latexpages/issues',
        'CI': 'https://github.com/xflr6/latexpages/actions',
    },
    packages=find_packages(),
    entry_points={'console_scripts': [
        'latexpages=latexpages.__main__:main',
        'latexpages-paginate=latexpages.__main__:main_paginate',
        'latexpages-clean=latexpages.__main__:main_clean'
    ]},
    package_data={'latexpages': ['template.tex', 'settings.ini']},
    zip_safe=False,
    platforms='any',
    python_requires='>=3.8',
    extras_require={
        'dev': ['flake8', 'pep8-naming', 'wheel', 'twine'],
        'test': ['coverage'],
    },
    long_description=pathlib.Path('README.rst').read_text(encoding='utf-8'),
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Printing',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
)
