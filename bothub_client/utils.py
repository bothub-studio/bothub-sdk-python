# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import ast
import inspect
import sys
import traceback


def traceback_to_string(exc, tb=None):
    _tb = tb or exc.__traceback__
    s = traceback.extract_stack()[:-3] + traceback.extract_tb(_tb)
    l = traceback.format_list(s)
    return ''.join(l) + '\\n  {} {}'.format(exc.__class__, exc)


def get_decorators(cls):
    decorators = {}

    def visit_FunctionDef(node):
        decorators[node.name] = []
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            args = [a.s for a in n.args] if hasattr(n, 'args') else []
            decorators[node.name].append((name, args))

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    _cls = cls if inspect.isclass(cls) else cls.__class__
    node_iter.visit(ast.parse(inspect.getsource(_cls)))
    return decorators
