\ProvidesClass{psf}

\LoadClass[
  twoside,%
  headings=small,%
  fontsize=11pt,%
  numbers=endperiod,%#
]{scrartcl}

% font encoding
\usepackage[T1]{fontenc}
\renewcommand{\encodingdefault}{T1}

% serif font
\usepackage{lmodern}

% page margins
\usepackage[%
  bindingoffset=5mm,%
  centering,%
  heightrounded,%
  headsep=10pt,%
]{geometry}

% page head, page foot
\usepackage{scrpage2}
\pagestyle{scrheadings}

% twoside
\AtEndDocument{\cleardoublepage}
\newcommand{\theend}{\makeatletter\global\let\@enddocumenthook\@empty\makeatother}

% font styles
\setkomafont{title}{\rmfamily\bfseries}

% mockup content
\usepackage{blindtext}

\endinput