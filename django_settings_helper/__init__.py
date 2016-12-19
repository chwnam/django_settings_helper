from __future__ import absolute_import
import os

try:
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    class ImproperlyConfigured(Exception):
        pass

from importlib import import_module
from re import compile as re_compile

var_expr = re_compile(r'^\s*export\s(?P<key>.+?)=((\"|\')?)(?P<val>.+?)((\"|\')?)\s*#[^#]*$')


def get_env(key, strict=False, default=None, type_cast=str):
    if strict and key not in os.environ:
        raise ImproperlyConfigured('Key \'{}\' not found in the environment variables'.format(key))

    value = os.environ.get(key=key, default=default)
    if type_cast == bool and value.capitalize() in ('True', 'False', 'Yes', 'No', '1', '0', 'On', 'Off'):
        return value.capitalize() in ('True', 'Yes', '1', 'On')
    return type_cast(value)


def env_from_file(path):
    if not os.path.exists(path):
        return

    with open(path) as fp:
        for line in fp:
            matched = var_expr.search(line)
            if not matched:
                continue
            key = matched.groupdict().get('key')
            val = matched.groupdict().get('val')
            if key and val:
                os.environ.setdefault(key, val)


def import_all(package, global_space):
    module = import_module(package)
    if module:
        global_space.update({k: v for k, v in module.__dict__.items() if not k.startswith('__')})
