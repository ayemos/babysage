import base64
from urllib.parse import urlparse

import boto3
import docker

from babysage.utils import find_project_root
from babysage.config import get_config


def deploy(dockerfile):
    aws_account_id = boto3.client('sts').get_caller_identity()['Account']
    ecr = boto3.client(service_name='ecr')
    resp = ecr.get_authorization_token(
        registryIds=[aws_account_id])
    token = resp['authorizationData'][0]['authorizationToken']
    proxy_endpoint = resp['authorizationData'][0]['proxyEndpoint']
    tag = f"babysage-{get_config('experiment_name')}"
    repository_tag = urlparse(proxy_endpoint).netloc + '/' + tag
    user, password = base64.b64decode(token).decode().split(':')

    client = docker.from_env()
    client.login(
        username=user,
        password=password,
        registry=proxy_endpoint)

    project_root = find_project_root()

    if project_root:
        dockerfile = dockerfile or 'Dockerfile'
        client.images.build(
            path=project_root,
            quiet=False,
            rm=True,
            tag=repository_tag,
            dockerfile=dockerfile)
        for l in client.images.push(repository_tag, stream=True, decode=True):
            print(l)
    else:
        raise Exception('''
        Current directry is not a babysage project directry (could not find `babysage.yml` file''')
