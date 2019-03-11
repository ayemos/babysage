import os

import docker

from babysage.utils import find_project_root, get_input_dir, get_output_dir
from babysage.config import get_config


def run_local(dockerfile):
    client = docker.from_env()

    project_root = find_project_root()

    if project_root:
        dockerfile = dockerfile or 'Dockerfile'
        tag = f"babysage-{get_config('experiment_name')}",
        client.images.build(
            path=project_root,
            quiet=False,
            rm=True,
            tag=tag,
            dockerfile=dockerfile)
        client.containers.run(
            tag,
            'train',
            volumes={
                os.path.join(project_root, 'input'): {
                    'bind': get_input_dir(), 'mode': 'rw'},
                os.path.join(project_root, 'output'): {
                    'bind': get_output_dir(), 'mode': 'rw'}})
    else:
        raise Exception('''
        Current directry is not a babysage project directry (could not find `babysage.yml` file''')
