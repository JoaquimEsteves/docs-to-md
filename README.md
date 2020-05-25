# doc2md

Automatically parse python docstrings and convert them to markdown!

## Installing

`pip install` and you're good to go!

## Instructions

Simply run the `docs2md.py` from the command line to interact with the ol' main function.

Note: Program uses f-strings, as such python `3.6` or above is required.

The command line arguments are as follow:

```bash
positional arguments:
  f                     File or directory to parse!

optional arguments:
  -h, --help            show this help message and exit
  -d [DOCS_DIR], --docs-dir [DOCS_DIR]
                        Documentation directory in which your .md files will
                        be saved. Defaults to [cwd]/docs
  -p, --just-print      Prints the results instead of creating a whole file!
  -s [SAVE_IMPORT], --save-import [SAVE_IMPORT]
                        Whether you'll want to save the imports to another
                        file. Simply place the path of the txt file you'll
                        want to save your imports to
  --test                Runs doctest!
```

As such, assuming you'll have a folder structure like so:

```
.
├── foo.py
├── blahbla
│   ├── __init__.py
│   └── blahblah.py
├── LICENSE
└── README.md
```

Running `python3 -m docs2md.py .` will produce the following:

```
.
├── docs
│   ├── foo.md
│   └── blahbla
│       ├── __init__.py
│       └── blahblah.py
├── foo.py
├── blahbla
│   ├── __init__.py
│   └── blahblah.py
├── LICENSE
└── README.md
```

### How does this work anyway?

If the input is a directory, `doc2md.py` will glob all of the files looking for python
files and then look for doctrings.

**Note**: That the program will also include the `__init__` and main files, as these
can include critical declarations.

The `yield_docstrings` function will use python's abstract syntax tree module to look
for docstrings near the following nodes:

  * FunctionDef:

`def foo()...`

  * AsyncFunctionDef:

`def async foo()...`

  * ClassDef:

`class foo:...`

  * Module:

`"""docstrings at the start of a file"""`

And automatically generate a simple markdown based on them.
Feel free to perouse this repo's docs folder, which was
naturally created using this tool.

The program will also look for the following nodes:

  * ImportFrom
  * Import

And mentions the fact that a python file imports from this or that
module.

(This is useful to keep track of dependencies, and you can save these
separately using the -s flag)

As of the moment of writting, the program does not yet include
global variables or data. Although I'm partial to including them
in a future update.
