# Module 'docs2md'
Parse Python source code and get or print docstrings.
## Imports
* ast
* itertools
* os.path
* typing
* textwrap

### Function 'yield_docstrings'
line 42

```python
def yield_docstrings(
    source: t.Union[t.IO[str], str], module: str = '<string>',
    import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[str]:
```
Parse Python source code from file or string and print docstrings.

For each class, method/function and module, the function prints a heading
with the type, name and line number and then the docstring with normalized
indentation.

The module name is determined from the filename, or, if the source is
passed as a string, from the optional `module` argument.

The line number refers to the first line of the docstring, if present,
or the first line of the class, funcion or method block, if there is none.
Output is ordered by line number :)

### Function 'parse_docstrings'
line 98

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
(<_ast.FunctionDef object at ...>, 'here_is_cool', 12, ...')
(<_ast.FunctionDef object at ...>, 'undocumented_function', 35, ...')
(<_ast.FunctionDef object at ...>, 'sub_yo', 24, ...')
(<_ast.ClassDef object at ...>, 'Blarg', 26, 'sub class ')
(<_ast.FunctionDef object at ...>, 'aze', 30, ...')

```

### Function 'get_imports'
line 190

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
