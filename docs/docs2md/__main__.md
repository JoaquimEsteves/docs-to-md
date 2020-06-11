# Module '__main__'
Handles argument parsing and file shenanigans
## Imports
* pathlib
* argparse
* contextlib
* doctest
* typing
* sys
* docs2md

### Function '_make_path_sane'
line 14

```python
def _make_path_sane(path: str) -> pth.Path:
```
Simple function that converts a path to a Pure (absolute) Path.
If the path isn't absolute, program assumes cwd()

### Function 'main'
line 27

```python
def main() -> None:
```
**UNDOCUMENTED**

### Function '_mini_main'
line 33

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
line 74

```python
def _glob_py_dirs(
    dir_to_analyse: pth.Path,
    original_docs_dir: pth.Path,
) -> t.Iterator[t.Tuple[pth.Path, pth.Path]]:
```
Globs a directory, looking for .py files 
