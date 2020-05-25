# -*- coding: utf-8 -*-
"""Parse Python source code and get or print docstrings."""

import ast
import sys

from itertools import groupby
from os.path import basename, splitext
import typing as t

from textwrap import dedent

# Types
# for python <= 3.7, we need to declare these at the top of the file
Node = t.Union[ast.ClassDef, ast.FunctionDef, ast.Module]
ImportNode = t.Union[ast.ImportFrom, ast.Import]

# This section describes how to translate Python objects to
# Markdown
_FUNCTION_TYPES: t.Dict[t.Type[ast.AST], str] = {
    ast.FunctionDef: '\n### Function',
    ast.AsyncFunctionDef: '\n### Async Function',
}
# The ** denote that Declare types include function types
# and that node types, include declare types
_DECLARE_TYPES: t.Dict[t.Type[ast.AST], str] = {
    **_FUNCTION_TYPES,
    ast.ClassDef: '\n## Class',
    ast.Module: '# Module',
}

_NODE_TYPES: t.Dict[t.Type[ast.AST], str] = {
    **_DECLARE_TYPES,
    ast.ImportFrom: "\nImports",
    ast.Import: "\nImports",
}


def yield_docstrings(
    source: t.Union[t.IO[str], str], module: str = '<string>',
    import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[str]:
    """ Parse Python source code from file or string and print docstrings.

    For each class, method/function and module, the function prints a heading with
    the type, name and line number and then the docstring with normalized
    indentation.

    The module name is determined from the filename, or, if the source is passed
    as a string, from the optional `module` argument.

    The line number refers to the first line of the docstring, if present,
    or the first line of the class, funcion or method block, if there is none.
    Output is ordered by line number :)

    """
    actual_source: str
    if hasattr(source, 'read'):
        file_source: t.IO[str] = t.cast(t.IO[str], source)
        filename = getattr(file_source, 'name', module)
        module = splitext(basename(filename))[0]
        actual_source = file_source.read()
    else:
        # We're dealing with a straight string
        # ie yield_docstrings('def (a:aze) -> None:...')
        actual_source = t.cast(str, source)
    # get the docstrings, and sort them by line number
    iter_docstrings = sorted(
        parse_docstrings(actual_source, import_file),
        key=lambda x: x[2])
    grouped = groupby(iter_docstrings, key=lambda tpl: (
        _NODE_TYPES[type(tpl[0])]
    ))

    first_import = True

    for type_, group in grouped:
        for _node, name, lineno, docstring in group:
            name = name if name else module
            if type_ == _NODE_TYPES[ast.Module]:
                yield f"{type_} '{name}'\n"
            elif type_ in (_NODE_TYPES[ast.ImportFrom], _NODE_TYPES[ast.Import]):
                if first_import:
                    first_import = False
                    yield "## Imports\n"
                yield f"* {name}"
            else:
                yield f"{type_} '{name}'\nline {lineno or '?'}\n\n"
            yield f"{docstring}\n" or '\n'


def parse_docstrings(
    source: t.Union[str], import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[t.Tuple[ast.AST, t.Any, int, str]]:
    """ Parse Python source code and yield a tuple of ast node instance, name,
        line number and docstring for each function/method, class and module.

        The line number refers to the first line of the docstring. If there is
        no docstring, it gives the first line of the class, funcion or method
        block, and docstring is None.


        Tests:
        ```python
        Example string with inner functions, classes, and module documentation!
        >>> example_string='''\""" Module documentation \"""
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
        ...     \""" typical docstring
        ...         - Args:
        ...             - a (str): example_input
        ...         - Returns:
        ...             - t[azeaze,azeaze]: Example of complicated return type
        ...     \"""
        ...
        ...     cache = {}
        ...     \""" doesn't care about docstrings not in class/function
        ...     \"""
        ...
        ...     def sub_yo(aze: str):
        ...         \""" sub function\"""
        ...
        ...     class Blarg:
        ...         \""" sub class \"""
        ...
        ...         def aze(self, a):
        ...             \""" sub-function of subclass \"""
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
    """
    tree = ast.parse(source)
    source_lines: t.List[str] = source.splitlines()
    for n in ast.walk(tree):
        if isinstance(n, tuple(_DECLARE_TYPES)):
            node: Node = t.cast(Node, n)
            docstring = ast.get_docstring(
                node, clean=True) or '**UNDOCUMENTED**'
            lineno = getattr(node, 'lineno', 0)
            if isinstance(node, tuple(_FUNCTION_TYPES)):
                # We're dealing with a function here!
                # Let's append its declaration here as python markdown
                # We tweak the line number to accomodate functions like:
                # def multiline(
                #     declaration,
                #     s,
                # ) -> something:
                lineno = node.body[0].lineno
                if node.lineno == lineno:
                    function_declaration = source_lines[lineno - 1:lineno]
                else:
                    function_declaration = source_lines[node.lineno - 1:lineno - 1]
                _function = dedent('\n'.join(function_declaration))
                docstring = (
                    f"```python\n{_function}\n```\n"
                    f"{docstring}"
                )
            yield (node, getattr(node, 'name', None), lineno, docstring)
        yield from get_imports(n, import_file)


def get_imports(
    node: ast.AST, file_to_save: t.Optional[t.IO[str]] = None
) -> t.Iterator[t.Tuple[ImportNode, t.Any, int, str]]:
    """ Handles the special case Import case

        Simply yields the imported modes.

        If node is like:

        ```python

        >>> node1 = 'Import os'
        >>> node2 = 'From yo.yoyo.aze import whatever'

        ```

        We'll yield 'os' and 'yo.yoyo.aze'

    """
    res: t.Tuple[ImportNode, t.Any, int, str]
    imports: str
    if isinstance(node, ast.ImportFrom):
        imports = node.module or '?'
        res = (node, f"{imports}", 0, "")
    elif isinstance(node, ast.Import):
        imports = ','.join([alias.name for alias in node.names])
        res = (node, f"{imports}", 0, "")
    else:
        return
    if file_to_save:
        file_to_save.write(f'├{imports}\n')
    yield res
