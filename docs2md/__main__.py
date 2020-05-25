import pathlib as pth
import argparse
from contextlib import ExitStack
import doctest
import typing as t
import sys

from .docs2md import yield_docstrings


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
        from itertools import chain
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
            print(f"Converting {python_file}")
            yield python_file, original_docs_dir / python_file.parent

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
    print(f"Saving docs in the folder {docs_dir}")
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


if __name__ == '__main__':
    main()
