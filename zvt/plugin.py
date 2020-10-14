# -*- coding: utf-8 -*-
import argparse
import os

from zvt.templates import all_tpls
from zvt.utils import now_pd_timestamp


def gen_plugin(entity_type, prefix: str = 'zvt', dir_path: str = '.', providers=['joinquant']):
    # generate project files
    project = f'{prefix}_{entity_type}'
    entity_class = entity_type.capitalize()
    project_path = os.path.join(dir_path, project)
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    current_time = now_pd_timestamp()

    for tpl in all_tpls(project=project):
        file_name = tpl[0]
        tpl_content = tpl[1].safe_substitute(project=project,
                                             entity_type=entity_type,
                                             entity_class=entity_class,
                                             providers=providers,
                                             year=current_time.year)
        file_path = os.path.join(project_path, file_name)

        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(tpl_content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entity', help='entity name', default='future')
    parser.add_argument('--prefix', help='project prefix', default='zvt')
    parser.add_argument('--dir', help='project directory', default='.')
    parser.add_argument('--providers', help='providers', default=['joinquant'], nargs='+')

    args = parser.parse_args()

    dir_path = args.dir
    entity = args.entity
    providers = args.providers
    prefix = args.prefix
    gen_plugin(prefix=prefix, dir_path=dir_path, entity_type=entity, providers=providers)


if __name__ == '__main__':
    main()
