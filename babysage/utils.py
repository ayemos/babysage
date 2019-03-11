import os
import pathlib


def find_project_root():
    root_dir = pathlib.Path(os.getcwd())

    for p in [root_dir] + list(root_dir.parents):
        if 'babysage.yml' in os.listdir(str(p)):
            return str(p)

    return None


def get_input_dir():
    return '/opt/ml/input/data/main'


def get_output_dir():
    return '/opt/ml/model'
