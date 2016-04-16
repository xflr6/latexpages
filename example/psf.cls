\ProvidesClass{psf}

\RequirePackage{kvoptions}
\SetupKeyvalOptions{prefix=@}
\DeclareBoolOption{last}
\DeclareDefaultOption{\@unknownoptionerror}
\ProcessKeyvalOptions*\relax

\PassOptionsToPackage{paper=a5}{typearea}
\LoadClass[
  twoside,%
  headings=small,%
  fontsize=11pt,%
  numbers=endperiod,%#
]{scrartcl}

% font encoding
\RequirePackage[T1]{fontenc}

% serif font
\RequirePackage{lmodern}

% page margins
\RequirePackage[%
  bindingoffset=5mm,%
  centering,%
  heightrounded,%
  headsep=10pt,%
]{geometry}

% page head, page foot
\RequirePackage{scrpage2}
\pagestyle{scrheadings}

% twoside
\if@last\else\AtEndDocument{\cleardoublepage}\fi

% font styles
\setkomafont{title}{\rmfamily\bfseries}

% mockup content
\RequirePackage{blindtext}

\endinput