# -*- coding: utf-8 -*-
import os
from typing import List

from zvt.contract import IntervalLevel, AdjustType
from zvt.utils.file_utils import list_all_files


def all_sub_modules(dir_path: str):
    """
    list all module name in specific directory

    :param dir_path:
    :return:
    """
    modules = []
    for entry in os.scandir(dir_path):
        if entry.is_dir() or (
                entry.path.endswith('.py') and not entry.path.endswith('__init__.py')):
            module_name = os.path.splitext(os.path.basename(entry.path))[0]
            # ignore hidden
            if module_name.startswith('.') or not module_name[0].isalpha():
                continue
            modules.append(module_name)
    return modules


def _remove_start_end(line: str, start='class ', end='('):
    if line.startswith(start) and (end in line):
        start_index = len(start)
        end_index = line.index(end)
        return line[start_index:end_index]
    if not start and (end in line):
        end_index = line.index(end)
        return line[:end_index]


def _get_interface(line):
    if line.startswith("class "):
        return _remove_start_end(line, "class ", "(")
    elif line.startswith("def "):
        return _remove_start_end(line, "def ", "(")


def all_sub_all(sub_module):
    return '''

# import all from submodule {0}
from .{0} import *
from .{0} import __all__ as _{0}_all
__all__ += _{0}_all'''.format(sub_module)


def gen_exports(path_dir='./domain', gen_flag='# the __all__ is generated'):
    files = list_all_files(dir_path=path_dir)
    for file in files:
        exports = []
        lines = []
        # read and generate __all__
        with open(file) as fp:
            line = fp.readline()
            while line:
                if line.startswith(gen_flag):
                    break
                lines.append(line)
                export = _get_interface(line)
                if export and export[0].isalpha():
                    exports.append(export)
                line = fp.readline()
        print(f'{file}:{exports}')
        lines.append(gen_flag)
        lines.append(f'\n__all__ = {exports}')

        # the package module
        basename = os.path.basename(file)
        if basename == '__init__.py':
            dir_path = os.path.dirname(file)
            modules = all_sub_modules(dir_path)
            if modules:
                lines.append('''

# __init__.py structure:
# common code of the package
# export interface in __all__ which contains __all__ of its sub modules''')
                for mod in modules:
                    lines.append(all_sub_all(mod))

        # write with __all__
        with open(file, mode='w') as fp:
            fp.writelines(lines)


# kdata schema rule
# 1)name:{entity_type}{level}Kdata
# 2)one db file for one schema

def gen_kdata_schema(pkg: str,
                     providers: List[str],
                     entity_type: str,
                     levels: List[IntervalLevel],
                     adjust_types: List[AdjustType] = [None],
                     entity_in_submodule: bool = False,
                     kdata_module='quotes'):
    tables = []

    base_path = './domain'

    if kdata_module:
        base_path = os.path.join(base_path, kdata_module)
    if entity_in_submodule:
        base_path = os.path.join(base_path, entity_type)

    for level in levels:

        for adjust_type in adjust_types:
            level = IntervalLevel(level)

            cap_entity_type = entity_type.capitalize()
            cap_level = level.value.capitalize()

            # you should define {EntityType}KdataCommon in kdata_module at first
            if level != IntervalLevel.LEVEL_TICK:
                kdata_common = f'{cap_entity_type}KdataCommon'
            else:
                kdata_common = f'{cap_entity_type}TickCommon'

            if adjust_type and (adjust_type != AdjustType.qfq):
                class_name = f'{cap_entity_type}{cap_level}{adjust_type.value.capitalize()}Kdata'
                table_name = f'{entity_type}_{level.value}_{adjust_type.value.lower()}_kdata'

            else:
                class_name = f'{cap_entity_type}{cap_level}Kdata'
                table_name = f'{entity_type}_{level.value}_kdata'

            tables.append(table_name)

            schema_template = f'''# -*- coding: utf-8 -*-
# this file is generated by gen_kdata_schema function, dont't change it
from sqlalchemy.ext.declarative import declarative_base

from zvt.contract.register import register_schema
from {pkg}.domain.{kdata_module} import {kdata_common}

KdataBase = declarative_base()


class {class_name}(KdataBase, {kdata_common}):
    __tablename__ = '{table_name}'


register_schema(providers={providers}, db_name='{table_name}', schema_base=KdataBase)

'''
            # generate the schema
            with open(os.path.join(base_path, f'{table_name}.py'), 'w') as outfile:
                outfile.write(schema_template)

        # generate the package
        pkg_file = os.path.join(base_path, '__init__.py')
        if not os.path.exists(pkg_file):
            package_template = '''# -*- coding: utf-8 -*-
'''
            with open(pkg_file, 'w') as outfile:
                outfile.write(package_template)

    # generate exports
    gen_exports('./domain')


# the __all__ is generated
__all__ = ['all_sub_modules', 'all_sub_all', 'gen_exports']
