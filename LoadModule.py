import importlib.abc
import os
import sys
import ast
def import_module(dir_path, module_name):
    filename = resolve_filename(dir_path, module_name)

    # I got test failures when I left this out, even though I thought it
    # was a responsibility of the loader.
    # If you know why this is, please enlighten me!
    if module_name in sys.modules:
        return sys.modules[module_name]

    return ASTFrobnicatingLoader(module_name, filename).load_module(module_name)


# in importlib, this function would be the job of the 'finder'
def resolve_filename(dir_path, module_name):
    filename = os.path.join(dir_path, *module_name.split('.'))
    if os.path.isdir(filename):
        filename = os.path.join(filename, '__init__.py')
    else:
        filename += '.py'
    return filename


class ASTFrobnicatingLoader(importlib.abc.FileLoader, importlib.abc.SourceLoader):
    def get_code(self, fullname):
        source = self.get_source(fullname)
        path = self.get_filename(fullname)

        parsed = ast.parse(source)
        # print(parsed)
        # self.frobnicate(parsed)

        return compile(parsed, path, 'exec', dont_inherit=True, optimize=0)

    def module_repr(self, module):
        return '<module {!r} from {!r}>'.format(module.__name__, module.__file__)