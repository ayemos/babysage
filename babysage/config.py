import os
import yaml

from babysage.utils import find_project_root

project_root = find_project_root()

if project_root:
    PROJECT_CONFIG = yaml.load(
        open(
            os.path.join(
                find_project_root(),
                'babysage.yml'), 'r').read())
else:
    raise Exception('''
    Can't find a suitable configuration file (babysage.yml) in this directory or any parent.''')


core_directory = os.path.expanduser(os.path.join('~', '.babysage'))

if not os.path.isdir(core_directory):
    os.makedirs(core_directory)

if os.path.isfile(os.path.join(core_directory, 'config.yml')):
    CORE_CONFIG = yaml.load(
        open(
            os.path.join(
                core_directory,
                'config.yml'), 'r').read())
else:
    CORE_CONFIG = {}


def get_config(key):
    return PROJECT_CONFIG.get(key, CORE_CONFIG.get(key, None))
