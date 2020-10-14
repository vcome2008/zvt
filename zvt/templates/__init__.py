# -*- coding: utf-8 -*-
import os
import string

from pkg_resources import resource_string

from zvt.utils.file_utils import list_all_files


def all_tpls(project: str):
    tpl_files = list_all_files(os.path.dirname(__file__), ext='template', return_base_name=True)
    tpls = []
    for tpl in tpl_files:
        data = resource_string(__name__, tpl)
        file_name = os.path.splitext(os.path.basename(tpl))[0]
        # we assure that line endings are converted to '\n' for all OS
        data = data.decode(encoding="utf-8").replace(os.linesep, "\n")

        # change path for specific file
        if file_name == 'kdata_common.py':
            file_name = f'{project}/domain/quotes/__init__.py'
        elif file_name == 'meta.py':
            file_name = f'{project}/domain/meta.py'
        elif file_name == 'fill_project.py':
            file_name = f'{project}/fill_project.py'

        tpls.append((file_name, string.Template(data)))
    return tpls
