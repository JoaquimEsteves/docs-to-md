# Module 'doc2md'
Parse Python source code and get or print docstrings.
## Imports
* ast
* sys
* itertools
* os.path
* typing
* pathlib
* argparse
* contextlib
* textwrap
* doctest
* glob
* itertools

### Function 'yield_docstrings'
line 47

```python
def yield_docstrings(
    source: t.Union[t.IO[str], str], module: str = '<string>',
    import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[str]:
```
Parse Python source code from file or string and print docstrings.

For each class, method/function and module, the function prints a heading with
the type, name and line number and then the docstring with normalized
indentation.

The module name is determined from the filename, or, if the source is passed
as a string, from the optional `module` argument.

The line number refers to the first line of the docstring, if present,
or the first line of the class, funcion or method block, if there is none.
Output is ordered by line number :)

### Function 'parse_docstrings'
line 99

```python
def parse_docstrings(
    source: t.Union[str], import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[t.Tuple[ast.AST, t.Any, int, str]]:
```
Parse Python source code and yield a tuple of ast node instance, name,
line number and docstring for each function/method, class and module.

The line number refers to the first line of the docstring. If there is
no docstring, it gives the first line of the class, funcion or method
block, and docstring is None.


Tests:
```python
Example string with inner functions, classes, and module documentation!
>>> example_string='''""" Module documentation """
... from whatever import *
... from aze.aze.aze import lel
... import os
... import sys
... def here_is_cool(
...     a: str
... ) -> t[
...     azeaze,
...     azeaze
... ]:
...     """ typical docstring
...         - Args:
...             - a (str): example_input
...         - Returns:
...             - t[azeaze,azeaze]: Example of complicated return type
...     """
...
...     cache = {}
...     """ doesn't care about docstrings not in class/function
...     """
...
...     def sub_yo(aze: str):
...         """ sub function"""
...
...     class Blarg:
...         """ sub class """
...
...         def aze(self, a):
...             """ sub-function of subclass """
...             ...
...
...
... def undocumented_function(aze):
...     pass'''
>>> for i in parse_docstrings(example_string): print(i)
(<_ast.Module object at ...>, None, 0, 'Module documentation ')
(<_ast.ImportFrom object at ...>, 'whatever', 0, '')
(<_ast.ImportFrom object at ...>, 'aze.aze.aze', 0, '')
(<_ast.Import object at ...>, 'os', 0, '')
(<_ast.Import object at ...>, 'sys', 0, '')
(<_ast.FunctionDef object at ...>, 'here_is_cool', 11, ...')
(<_ast.FunctionDef object at ...>, 'undocumented_function', 34, ...')
(<_ast.FunctionDef object at ...>, 'sub_yo', 23, ...')
(<_ast.ClassDef object at ...>, 'Blarg', 26, 'sub class ')
(<_ast.FunctionDef object at ...>, 'aze', 29, ...')

```

### Function 'get_imports'
line 192

```python
def get_imports(
    node: ast.AST, file_to_save: t.Optional[t.IO[str]] = None
) -> t.Iterator[t.Tuple[ImportNode, t.Any, int, str]]:
```
Handles the special case Import case

Simply yields the imported modes.

If node is like:

```python

>>> node1 = 'Import os'
>>> node2 = 'From yo.yoyo.aze import whatever'

```

We'll yield 'os' and 'yo.yoyo.aze'

### Function 'main'
line 224

```python
def main() -> None:
```
**UNDOCUMENTED**

### Function '_mini_main'
line 230

```python
def _mini_main(
    file_to_analyse: pth.Path,
    just_print: bool,
    save_import: t.Optional[str],
    docs_dir: pth.Path,
) -> None:
```
main handles the argparse and all those shenanigans.
_mini_main does the _actual_ function calls and opening of the
files.

We separate the concerns just so we can handle the case in which
main receives a directory with python files instead of a simple
`.py`

It's also useful to note, since people read code top to bottom,
and this is the actual 'workhorse' function

### Function '_glob_py_dirs'
line 276

```python
def _glob_py_dirs(
    dir_to_analyse: pth.Path,
    original_docs_dir: pth.Path,
) -> t.Iterator[t.Tuple[pth.Path, pth.Path]]:
```
**UNDOCUMENTED**

### Function '_make_path_sane'
line 351

```python
def _make_path_sane(path: str) -> pth.Path:
```
Simple function that converts a path to a Pure (absolute) Path.
If the path isn't absolute, program assumes cwd()
