# setup.py

from setuptools import setup, find_packages

setup(
    name='latexpages',
    version='0.6.3.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Combine LaTeX docs into a single PDF',
    keywords='pdfpages parallel compilation proceedings',
    license='MIT',
    url='https://github.com/xflr6/latexpages',
    packages=find_packages(),
    package_data={'latexpages': ['template.tex', 'settings.ini']},
    zip_safe=False,
    entry_points={'console_scripts': [
        'latexpages=latexpages.__main__:main',
        'latexpages-paginate=latexpages.__main__:main_paginate',
        'latexpages-clean=latexpages.__main__:main_clean'
    ]},
    platforms='any',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Printing',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
)
