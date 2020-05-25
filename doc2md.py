# -*- coding: utf-8 -*-
"""Parse Python source code and get or print docstrings."""

__all__ = ("yield_docstrings", "parse_docstrings", "get_imports", "main",)

import ast
import sys

from itertools import groupby
from os.path import basename, splitext
import typing as t
import pathlib as pth
import argparse
from contextlib import ExitStack
from textwrap import dedent
import doctest
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

    for type_, group in grouped:
        for _node, name, lineno, docstring in group:
            name = name if name else module
            if type_ == _NODE_TYPES[ast.Module]:
                yield f"{type_} '{name}'\n"
            elif type_ in (_NODE_TYPES[ast.ImportFrom], _NODE_TYPES[ast.Import]):
                yield f"{type_} '{name}'"
            else:
                yield f"{type_} '{name}'\nline {lineno or '?'}\n\n"
            yield f"{docstring}\n" or '\n'


def parse_docstrings(
    source: t.Union[str], import_file: t.Optional[t.IO[str]] = None
) -> t.Iterator[t.Tuple[ast.AST, t.Any, int, str]]:
    """Parse Python source code and yield a tuple of ast node instance, name,
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
    (<_ast.FunctionDef object at ...>, 'here_is_cool', 11, ...')
    (<_ast.FunctionDef object at ...>, 'undocumented_function', 34, ...')
    (<_ast.FunctionDef object at ...>, 'sub_yo', 23, ...')
    (<_ast.ClassDef object at ...>, 'Blarg', 26, 'sub class ')
    (<_ast.FunctionDef object at ...>, 'aze', 29, ...')
    
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
            if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Str)):
                # If the body is an expression, we gotta do some tweaking
                # of the lineno
                # this is to accommodate:
                # def multiline(
                #     declaration,
                #     s,
                # ) -> something:
                lineno = (node.body[0].lineno
                          - len(node.body[0].value.s.splitlines()))
            if isinstance(node, tuple(_FUNCTION_TYPES)):
                # We're dealing with a function here!
                # Let's append its declaration here as python markdown
                # We tweak the line number, for reasons similar to the
                # ones explained previously
                if node.lineno == lineno:
                    function_declaration = source_lines[lineno - 1:lineno]
                else:
                    function_declaration = source_lines[node.lineno - 1:lineno]
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


def main() -> None:
    def _mini_main(
        file_to_analyse: pth.Path,
        just_print: bool,
        save_import: t.Optional[str],
        docs_dir: pth.Path,
    ) -> None:
        """ main handles the argparse and all those shenanigans.
            _mini_main does the _actual_ function calls and opening of the
            files.

            We separate the concerns just so we can handle the case in which
            main receives a directory with python files instead of a simple
            `.py`

            It's also useful to note, since people read code top to bottom,
            and this is the actual 'workhorse' function
        """
        with ExitStack() as file_stack:
            # ExitStack is just so we don't have to have lots of with statements
            # on top of each other like `with A() as X, B() as Y, C() as Z:`
            # itjustworks.jpg
            # the funny greek letter is an alias
            docs_dir.mkdir(parents=True, exist_ok=True)
            ε = file_stack.enter_context  # pylint: disable=no-member
            fp = ε(open(file_to_analyse, 'r', encoding='utf-8'))
            import_fl = None
            if save_import:
                import_fl = ε(
                    open(_make_path_sane(save_import), 'a+', encoding='utf-8')
                )
                import_first_line = (f'\n┌{file_to_analyse} IMPORTS\n')
                import_fl.write(import_first_line)
            if just_print:
                for line in yield_docstrings(fp, import_file=import_fl):
                    print(line)
            else:
                md = ε(
                    open(f'{docs_dir}/{file_to_analyse.stem}.md',
                         'w', encoding='utf-8')
                )
                for line in yield_docstrings(fp, import_file=import_fl):
                    md.write(line)
            if import_fl:
                import_fl.write(
                    f"└{'─' * len(import_first_line)}\n"
                    "\n"
                )

    def _glob_py_dirs(
        dir_to_analyse: pth.Path,
        original_docs_dir: pth.Path,
    ) -> t.Iterator[t.Tuple[pth.Path, pth.Path]]:
        from glob import iglob
        from itertools import repeat, chain
        # We give it a spinner, as this'll take a while...
        spinner = repeat('|/-\\')
        python_files = dir_to_analyse.rglob('*.py')
        print(
            "I'm about to parse the following for python files"
        )
        for i in python_files:
            print(i)
        inpt = input('Are you sure you want to continue? Y - for yes\n')
        if inpt not in ('y', 'Y'):
            print('Goodbye 😘')
            return  # typing: ignore
        python_files = dir_to_analyse.rglob('*.py')
        for python_file in python_files:
            sys.stdout.write(next(spinner))
            yield python_file, original_docs_dir / python_file.parent
            sys.stdout.flush()
            sys.stdout.write('\b')

    parser = argparse.ArgumentParser(description='Convert Python to markdown!')
    parser.add_argument('f',
                        help='File or directory to parse!')
    parser.add_argument(
        '-d', "--docs-dir", nargs="?",
        default=pth.Path.cwd() / 'docs',
        help=(
            "Documentation directory in which your .md files will be saved. "
            "Defaults to [cwd]/docs"
        )
    )
    parser.add_argument(
        '-p', "--just-print", action="store_true",
        # default=None,
        help=(
            "Prints the results instead of creating a whole file!"
        )
    )
    parser.add_argument(
        '-s', '--save-import', nargs='?',
        # default=None,
        help=(
            "Whether you'll want to save the imports to another file.\n"
            "Simply place the path of the txt file you'll want to save your "
            "imports to"
        )
    )
    parser.add_argument(
        '--test', action="store_true",
        # default=None,
        help=(
            "Runs doctest!"
        )
    )
    if '--test' in sys.argv:
        doctest.testmod(optionflags=doctest.ELLIPSIS)
        return

    args = parser.parse_args()

    file_to_analyse = _make_path_sane(args.f)
    docs_dir = _make_path_sane(args.docs_dir)
    # Creates the docs_dir (if it doesn't exist...)
    if file_to_analyse.is_dir():
        # Well..shit!
        for sub_python_file, new_doc_dir in _glob_py_dirs(
            file_to_analyse,
            docs_dir
        ):
            _mini_main(sub_python_file,
                       args.just_print,
                       args.save_import,
                       new_doc_dir)
        return
    _mini_main(file_to_analyse, args.just_print, args.save_import, docs_dir)


def _make_path_sane(path: str) -> pth.Path:
    """ Simple function that converts a path to a Pure (absolute) Path.
        If the path isn't absolute, program assumes cwd()
    """
    proper_path = pth.Path(path)
    if proper_path.exists():
        return proper_path
    if not proper_path.is_absolute():
        # Eek, proper_path doesn't exist, well assume user is thinking of the cwd
        proper_path = pth.Path.cwd() / proper_path
    return proper_path


if __name__ == '__main__':
    if not sys.flags.interactive:
        main()
