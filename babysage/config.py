import os
import pathlib
import yaml


root_dir = pathlib.Path(os.getcwd())


for p in root_dir + root_dir.parents:
    if 'babysage.yml' in os.listdir(p):
        CONFIG = yaml.load(open('babysage.yml', 'r').read())

raise Exception('''
Can't find a suitable configuration file (babysage.yml) in this directory or any parent.''')


def get_config(key):
    return CONFIG[key]
