Latexpages
==========

|PyPI version| |License| |Supported Python| |Format|

|Build| |Codecov|

This tool automates compiling LaTeX document collections (for working papers,
proceedings, etc.) into a single combined PDF file using the pdfpages_ package.

Create an **INI file** giving the name and parts of your collection and build
it with the ``latexpages`` command-line utility.

``latexpages`` will start one parallel typesetting process per core for
speedup.

As each part is typeset independently, this allows to combine documents that
cannot be merged into a single master-document (use of incompatible
packages/options, latex-dvips-ps2pdf vs. pdflatex, etc.).


Links
-----

- GitHub: https://github.com/xflr6/latexpages
- PyPI: https://pypi.org/project/latexpages/
- Issue Tracker: https://github.com/xflr6/latexpages/issues
- Download: https://pypi.org/project/latexpages/#files


Installation
------------

This package runs under Python 3.6+, use pip_ to install:

.. code:: bash

    $ pip install latexpages

The compilation requires a TeX distribution (e.g. `TeX Live`_ or MikTeX_) and
either latexmk_ or MikTeX's texify_ utility being available on your system.

The optional automatic page numbering (see below) requires either the
``pdfinfo`` command-line utility (included in poppler_-utils,
miktex-poppler-bin_, xpdf_), or the  pdftk_ command-line utility (both
available cross-platform).


Usage
-----

Create a working directory holding your plain-text INI file with the latexpages
configuration. Put all your documents into subdirectories with the same name as
the corresponding ``.tex`` file:

::

    collection/
        latexpages.ini
        article1/
            article1.tex
            references.bib
        article2/
            article2.tex
            ...

Note: the directory names cannot contain spaces.

Edit the INI file to configure the parts, their order and various other
options:

.. code:: ini

    [make]
    name = MY_COLL
    directory = _output
    
    [parts]
    mainmatter = 
      article1
      article2

The following will typeset all parts, copy their PDFs to the output directory,
and combine them into a single PDF. By default, this also creates a 2-up
version:

.. code:: bash

    $ latexpages latexpages.ini

Check the `example directory`_ in the source distribution for a working
complete example. 


Invocation
----------

Check the usage of the ``latexpages`` command:

.. code:: bash

    $ latexpages --help
    usage: latexpages [-h] [--version] [-c {latexmk,texify}] [--keep]
                      [--only <part>] [--processes <n>]
                      [filename]
    
    Compiles and combines LaTeX docs into a single PDF file
    
    positional arguments:
      filename             INI file configuring the parts and output options
                           (default: latexpages.ini in the current directory)
    
    optional arguments:
      -h, --help           show this help message and exit
      --version            show program's version number and exit
      -c {latexmk,texify}  use latexmk.pl or texify (default: guess from platform)
      --keep               keep combination document(s) and their auxiliary files
      --only <part>        compile the given part without combining
      --processes <n>      number of parallel processes (default: one per core)


Pagination
----------

The following command goes trough all main documents and **updates the page
number** in the first ``\setcounter{page}{<number>}`` line of the source
according to the page count of the preceding documents' compiled PDFs.

.. code:: bash

    $ latexpages-paginate latexpages.ini

Make sure either the ``pdfinfo`` command-line tool (poppler_/xpdf_) or the
``pdftk`` executable from pdftk_ is available on your systems' path.

To use a different pattern for finding the ``\setcounter`` lines, set the
``update`` option in the ``paginate`` section of your INI file to a suitable
`regular expression`_.

.. code:: ini

    [paginate]
    update = \\setcounter\{page\}\{(\d+)\}


To also update the page numbers in your **table of contents**, put the
corresponding part name in the ``paginate`` section of your INI file.

Directory structure:

::

    collection/
        latexpages.ini
        prelims/
            prelims.tex
        article1/
            article1.tex
            ...

Configuration:

.. code:: ini

    [parts]
    frontmatter =
      prelims
    mainmatter = 
      article1
      article2

    [paginate]
    contents = prelims

By default, ``latexpages-paginate`` will search and update
``\startpage{<number>}`` lines in the source. To use this as marker, define and
use a corresponding LaTeX-command in your table of contents, e.g.
``\newcommand{\startpage}[1]{#1}``. A complete example is in the `example
directory`_

To use a different pattern for finding the table of contents lines, change
the `regular expression`_ in the ``replace`` option.

.. code:: ini

    [paginate]
    replace = \\startpage\{(\d+)\}


Check the usage of the ``latexpages-paginate`` command:

.. code:: bash

    $ latexpages-paginate --help
    usage: latexpages-paginate [-h] [--version] [filename]
    
    Computes and updates start page numbers in compiled parts and contents
    
    positional arguments:
      filename    INI file configuring the parts and paginate options
                  (default: latexpages.ini in the current directory)
    
    optional arguments:
      -h, --help  show this help message and exit
      --version   show program's version number and exit


Advanced options
----------------

Below are annotated INI file sections showing the **default options** for all
available configuration settings.

The ``make`` section sets the **names** and file name templates_ for the
results:

.. code:: ini

    [make]
    name = COLL              # name of the resulting PDF file
    directory = _output      # directory to copy/put the results
    
    two_up = __%(name)s_2up  # name of the 2-up version PDF file
    make_two_up = true       # create a 2-up version (yes/no)
    
    # templates for the name of the copied part PDF files for each
    # of the three possible groups (frontmatter, mainmatter, extras)
    # available substitutions:
    #   (note that the percent-sign must be doubled here)
    #   %%(name)s    name of the result file (see above)
    #   %%(part)s    name of the part directory/filename
    #   %%(index0)d  zero-based index inside group
    #   %%(index1)d  one-based index inside group
    
    frontmatter = _%%(name)s_%%(part)s
    mainmatter = %%(name)s_%%(index1)02d_%%(part)s
    extras = %(frontmatter)s


The ``parts`` section gives **space-delimited** lists of parts to compile
and/or include:

.. code:: ini

    [parts]
    frontmatter =  # include at the beginning, roman page numbering 
    mainmatter =   # include after frontmatter, arabic page numbering
    extras =       # compile and copy only (e.g. a separate cover page)
    
    use_dvips =    # use latex -> dvips -> ps2pdf for these parts
                   # instead of pdflatex (e.g. pstricks usage)
    
    # pull the first mainmatter part into the roman page numbering area
    first_to_front = false


The ``substitute`` section fills the template that is used to create the
combination document. With the default template, this allows to set the PDF
**meta data**:

.. code:: ini

    [substitute]   
    # options for \usepackage{hyperref}
    author =       # pdfauthor
    title =        # pdftitle
    subject =      # pdfsubject
    keywords =     # pdfkeywords


The ``template`` section allows to customize the details of the **combination
document**:

.. code:: ini

    [template]
    filename =         # use a custom template
    filename_two_up =  # different template for 2-up version
    
    class = scrartcl   # use this documentclass
    
    # documentclass options for combination and 2-up version
    options = paper=a5    
    options_two_up = paper=a4,landscape
    
    # includepdfmerge options for combination and 2-up version
    include = fitpaper
    include_two_up = nup=2x1,openright


The ``compile`` section allows to change the **invocation options** of the
compilation commands used.

.. code:: ini

    [compile]
    latexmk = -silent                   # less verbose 
    
    texify = --batch --verbose --quiet  # halt on error, less verbose
    # only used with texify (latexmk calls these automatically)
    dvips = -q
    ps2pdf =


Finally, the ``paginate`` section controls ``latexpages-paginate`` (see above).

.. code:: ini

    [paginate]
    update = \\setcounter\{page\}\{(\d+)\}  # search/update regex
    contents =                              # part with table of contents
    replace = \\startpage\{(\d+)\}          # toc line search/update regex


See also
--------

- https://www.ctan.org/topic/compilation
- https://www.ctan.org/topic/confproc
- https://www.ctan.org/pkg/pdfpages
- https://www.ctan.org/pkg/confproc
- http://go.warwick.ac.uk/pdfjam
- http://community.coherentpdf.com
- https://github.com/JacksonLLee/cls-proceedings


License
-------

``latexpages`` is distributed under the `MIT license`_.


.. _pdfpages: https://www.ctan.org/pkg/pdfpages
.. _pip: https://pip.readthedocs.io

.. _TeX Live: https://www.tug.org/texlive/
.. _MikTeX: https://miktex.org
.. _latexmk: http://personal.psu.edu/jcc8/software/latexmk-jcc/
.. _texify: https://docs.miktex.org/manual/texifying.html
.. _poppler: https://poppler.freedesktop.org
.. _miktex-poppler-bin: https://www.ctan.org/search/?phrase=miktex-poppler-bin&ext=true&FILES=on
.. _xpdf: http://foolabs.com/xpdf/
.. _pdftk: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
.. _regular expression: https://docs.python.org/2/library/re.html

.. _example directory: https://github.com/xflr6/latexpages/tree/master/example

.. _templates: https://docs.python.org/2/library/stdtypes.html#string-formatting

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/latexpages.svg
    :target: https://pypi.org/project/latexpages/
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/latexpages.svg
    :target: https://pypi.org/project/latexpages/
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/latexpages.svg
    :target: https://pypi.org/project/latexpages/
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/latexpages.svg
    :target: https://pypi.org/project/latexpages/
    :alt: Format

.. |Build| image:: https://github.com/xflr6/latexpages/actions/workflows/build.yaml/badge.svg?branch=master
    :target: https://github.com/xflr6/latexpages/actions/workflows/build.yaml?query=branch%3Amaster
    :alt: Build
.. |Codecov| image:: https://codecov.io/gh/xflr6/latexpages/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/xflr6/latexpages
    :alt: Codecov
