#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2024 Kurt Micallef & Marc Tanti
#
# This file is part of malti project.
'''
Automatically generate the API documentation.
'''

import os
import shutil
import ast
from typing import Any
import malti


#########################################
def generate(
    code_path: str,
    doc_path: str,
    ancestors: list[str],
) -> tuple[list[str], list[str]]:
    '''
    Generate a Sphinx .rst file for every .py file.

    :param code_path: The path to the code files.
    :param doc_path: The path to the Sphinx document files.
    :param ancestors: The list of folder ancestors that contain the files in ``code_path``.
    :return: A pair containing a list of directories and a list of Python files in ``code_path``.
    '''
    code_names: list[str] = []
    dir_names: list[str] = []
    if len(ancestors) == 0:
        dir_names = ['malti']
    else:
        for name in os.listdir(code_path):
            path = os.path.join(code_path, name)
            if os.path.isfile(path) and name.endswith('.py') and name not in [
                '__init__.py',
            ]:
                code_names.append(name)
            elif os.path.isdir(path) and name not in [
                '__pycache__',
            ]:
                dir_names.append(name)

    for dir_name in dir_names:
        new_doc_path = os.path.join(doc_path, dir_name)
        new_code_path = os.path.join(code_path, dir_name)

        (child_dir_names, child_code_names) = generate(
            new_code_path, new_doc_path, ancestors + [dir_name]
        )

        if len(child_dir_names) + len(child_code_names) > 0:
            init_path = os.path.join(code_path, dir_name, '__init__.py')
            with open(init_path, 'r', encoding='utf-8') as f:
                tree: Any = ast.parse(f.read())
                if len(tree.body) == 0:
                    raise AssertionError(f'Missing docstring in {init_path}.')
                if not isinstance(tree.body[0].value, ast.Str):
                    raise AssertionError(f'Missing docstring in {init_path}.')
                description: str = tree.body[0].value.value.strip()

            os.makedirs(doc_path, exist_ok=True)
            with open(
                os.path.join(doc_path, f'{dir_name}.rst'),
                'w', encoding='utf-8', newline='\n',
            ) as f:
                print(f'''\
{dir_name}
{'='*len(dir_name)}

{description}

.. toctree::
    :maxdepth: 1
''', file=f)
                for child in child_code_names:
                    print(f'    {dir_name}/{child[:-3]}.rst', file=f)
                for child in child_dir_names:
                    print(f'    {dir_name}/{child}', file=f)

    for code_name in code_names:
        name = code_name[:-3]
        fully_qualified_code_name = '.'.join(ancestors + [name])
        os.makedirs(doc_path, exist_ok=True)
        with open(
            os.path.join(doc_path, f'{name}.rst'),
            'w', encoding='utf-8', newline='\n',
        ) as f:
            print(f'''\
{name}.py
{'='*(len(name) + 3)}

.. automodule:: {fully_qualified_code_name}
    :members:
    :show-inheritance:
    :inherited-members:
    :special-members:
    :exclude-members: __weakref__
''', file=f)

    return (dir_names, code_names)


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    doc_dir = os.path.abspath(os.path.join(malti.path, '..', '..', 'docs', 'source'))

    try:
        os.remove(os.path.join(doc_dir, 'malti.rst'))
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree(os.path.join(doc_dir, 'malti'))
    except FileNotFoundError:
        pass

    with open(
        os.path.join(doc_dir, 'index.rst'),
        'w', encoding='utf-8', newline='\n',
    ) as f:
        print('''\
Welcome to malti's documentation!
=================================

.. toctree::
   :maxdepth: 1

   usage
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
''', file=f)

    try:
        with open(
            os.path.join(doc_dir, 'usage.rst'),
            'x', encoding='utf-8', newline='\n',
        ) as f:
            print('''\
User documentation
==================

''', file=f)
    except FileExistsError:
        pass

    with open(
        os.path.join(doc_dir, 'api.rst'),
        'w', encoding='utf-8', newline='\n',
    ) as f:
        print('''\
API
===

This is the code's API documentation where you can browse to any module and read its documentation.

.. toctree::
    :maxdepth: 1

    ''' + (
       '' if set(os.listdir(os.path.join(malti.path))) - {'__pycache__'} == {'__init__.py'}
       else 'malti'
   ) + '''
''', file=f)


    generate(
        os.path.abspath(os.path.join(malti.path, '..')),
        doc_dir,
        [],
    )


#########################################
if __name__ == '__main__':
    main()
