#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2024 Kurt Micallef & Marc Tanti
#
# This file is part of malti project.
'''
Validate the project files.
'''

import os
import argparse
import ast
from typing import Any
import malti


#########################################
def check_init(
    code_path: str,
) -> None:
    '''
    Check for any missing __init__.py files.

    :param code_path: The path to the code files.
    '''
    names = os.listdir(code_path)

    if '__init__.py' not in names:
        raise AssertionError(f'Missing __init__.py in {code_path}.')

    for name in names:
        new_path = os.path.join(code_path, name)
        if os.path.isdir(new_path) and name not in [
            '__pycache__',
        ]:
            check_init(new_path)


#########################################
def check_docstrings_tree(
    tree: Any,
    path: str,
) -> None:
    '''
    Check the docstrings in a single file represented as an abstract syntax tree.
        Used to recursively check the docstrings in classes and functions in the tree.

    :param tree: The abstract syntax tree of the code file being checked (produced by
        ast.parse).
    :param path: The path to the file being checked (used for error messages).
    '''
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if (
                not isinstance(node.body[0], ast.Expr)
                or not isinstance(node.body[0].value, ast.Str)
            ):
                raise AssertionError(
                    f'Missing docstring in class {node.name} on line {node.lineno}'
                    f' in file {path}.'
                )
            check_docstrings_tree(node, path)

        elif isinstance(node, ast.FunctionDef):
            name: str = node.name
            line_num: int = node.lineno
            args: list[str] = [arg.arg for arg in node.args.args if arg.arg != 'self']
            assert node.returns is not None
            has_return = (
                not isinstance(node.returns, ast.NameConstant)
                or node.returns.value is not None
            )
            if (
                not isinstance(node.body[0], ast.Expr)
                or not isinstance(node.body[0].value, ast.Str)
            ):
                raise AssertionError(
                    f'Missing docstring in function {name} on line {line_num} in file {path}.'
                )
            docstring: str = node.body[0].value.s

            args_mentioned = []
            return_mentioned = False
            for line in docstring.split('\n'):
                line = line.strip()
                if line.startswith(':param '):
                    arg = line.split(' ')[1][:-1]
                    args_mentioned.append(arg)
                if line.startswith(':return:'):
                    return_mentioned = True
            if args != args_mentioned:
                raise AssertionError(
                    f'The docstring in function {name} on line {line_num}'
                    f' in file {path} does not match the function\'s arguments.'
                    ' Arguments in docstring but not in function: {}.'
                    ' Arguments in function but not in docstring: {}.'
                    .format(
                        sorted(set(args_mentioned) - set(args)),
                        sorted(set(args) - set(args_mentioned)),
                    )
                )
            if has_return != return_mentioned:
                raise AssertionError(
                    f'The docstring in function {name} on line {line_num}'
                    f' in file {path} does not match the function\'s return annotation.'
                )


#########################################
def check_docstrings_file(
    path: str,
) -> None:
    '''
    Check the docstrings in a single file.

    :param path: The path to the file being checked (used for error messages).
    '''
    with open(path, 'r', encoding='utf-8') as f:
        tree: Any = ast.parse(f.read())

    if (
        not isinstance(tree.body[0], ast.Expr)
        or not isinstance(tree.body[0].value, ast.Str)
    ):
        raise AssertionError(
            f'Missing module docstring in file {path}.'
        )

    check_docstrings_tree(tree, path)


#########################################
def check_docstrings_dir(
    code_path: str,
) -> None:
    '''
    Check for any missing Sphinx documents together.

    :param code_path: The path to the code files.
    '''
    names = os.listdir(code_path)

    for name in names:
        new_path = os.path.join(code_path, name)

        if os.path.isfile(new_path) and name.endswith('.py') and name not in [
            '__init__.py',
        ]:
            check_docstrings_file(new_path)

        if os.path.isdir(new_path) and name not in [
            '__pycache__',
        ]:
            check_docstrings_dir(new_path)


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description='Validate the project files.'
    )

    parser.parse_args()

    check_init(os.path.abspath(os.path.join(malti.path, '..', '..', 'tests')))
    check_init(malti.path)

    check_docstrings_dir(os.path.abspath(os.path.join(malti.path, '..', '..', 'tools')))
    check_docstrings_dir(os.path.abspath(os.path.join(malti.path, '..', '..', 'tests')))
    check_docstrings_dir(malti.path)


#########################################
if __name__ == '__main__':
    main()
