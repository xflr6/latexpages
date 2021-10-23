Changelog
=========


Version 0.7 (in development)
----------------------------

Drop Python 2 support.

Tag Python 3.10 support.


Version 0.6.8
-------------

Fix example: replace ``scrpage2`` with successor ``scrlayer-scrpage``.

Drop Python 3.5 support and tag Python 3.9 support.


Version 0.6.7
-------------

Tag Python 3.8 support.


Version 0.6.6
-------------

Add description for ``latexpages-clean``.

Drop Pytjon 3.4 support.


Version 0.6.5
-------------

Tag Python 3.7 support, stop reusing ``subprocess.STARTUPINFO`` instances.


Version 0.6.4
-------------

Add ``python_requires``, update package scaffolding and project links.


Version 0.6.3
-------------

Drop Pyton 3.3 support.

Include license file in wheel.


Version 0.6.2
-------------

Fixed clean except pattern with subdirectory not recognized.


Version 0.6.1
-------------

Drop workaround for ``wheel`` ``console_script`` launcher bug
under Windows (pypa/pip#1891) from docs.

Enable multiprocessing in ``__main__.py`` invocation for 2.7.11+ under Windows.


Version 0.6
-----------

Use more widely deployed ``pdfinfo`` command (``poppler-utils``,
``miktex-poppler-bin``, ``xpdf``) as default page counting backend for pagination
where available (fall back to``pdftk``).

Hide render/pipe subrocess console window on Windows when invoked from
non-console process (e.g. from IDLE).


Version 0.5.1
-------------

Fixed broken Python 3 compatibility.

Adapted clean command for make-like invocation.

Made author and title extraction regex for wip contents creation feature
configurable and compatible with optional arguments.


Version 0.5
-----------

Changed command line invocation: number of processes is now a keyword parameter
(``--processes <n>``) instead of an optional positional parameter.

Simplified invocation: The filename argument for the commands ``latexpages``
and latexpages-paginate is now optional and defaults to ``latexpages.ini``
in the current directory (like make defaults to use ``Makefile``).

Added clean except config setting for excluding files from clean command.


Version 0.4.3
-------------

Fix potential ``latexpages-paginate`` bug with custom replace regex.


Version 0.4.2
-------------

Correct omission of the actual bugfix intended for 0.4.1.


Version 0.4.1
-------------

Fix ``latexpages-paginate`` bug with custom update regex not ending with ``}``
or similar.

Make better use of custom LaTeX class in example.


Version 0.4
-----------

Added ``--only <part>`` command-line option for single article compiling.

Bypass ``multiprocessing.Pool`` when single-process rendering is requested.

Workaround multiprocessing issues with ``KeyBoardInterrupt``.

Improved ``__main__.py`` invocation support on Windows.
Document workaround for launcher installation issues.


Version 0.3.2
-------------

Fixed broken manual install due to ``setuptools`` automatic ``zip_safe``
analysis not working as expected.


Version 0.3.1
-------------

Added wheel.


Version 0.3
-----------

Added cleaning command for deleting intermediate and output files.

Allow to set default number of processes and engine in config file.

Added support for ``python -m latexpages`` invocation.


Version 0.2.2
-------------

More informative exception on failed texify/latexmk/pdftk execution.

Improved example to leave out the empty page at the end.


Version 0.2.1
-------------

Documentation fixes.

Improved example.


Version 0.2
-----------

Added automatic page number computation with table of contents update.

Added INI settings for custom compile commands options.

Added setting for custom 2-up template.

Support ``utf-8`` encoded templates.

Fixed custom template loading.


Version 0.1
-----------

Initial release.
