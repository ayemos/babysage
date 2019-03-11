import os
import pkg_resources

import boto3
from jinja2 import Template


def init(name, ecr_repo_name, s3_bucket_name, execution_role_arn, region):
    aws_account_id = boto3.client('sts').get_caller_identity()['Account']

    print(f'Creating babysage experiment {name}.')

    session = boto3.session.Session()
    region_name = region or session.region_name
    ecr = session.client('ecr')
    ecr_repo_name = ecr_repo_name or f'babysage-{name}'
    ecr_repo_arn = f'{aws_account_id}.dkr.ecr.{region_name}.amazonaws.com/{ecr_repo_name}'

    try:
        resp = ecr.describe_repositories(repositoryNames=[ecr_repo_name])
        ecr_repo_arn = resp['repositories'][0]['repositoryArn']
    except Exception as e:
        print(e.__dict__)
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            print(f'ECR repositroy {ecr_repo_arn} doesn\'t seem to be exist')
            if input('Can I create one? [y/N]') in 'yY':
                resp = ecr.create_repository(repositoryName=ecr_repo_name)

    s3 = session.client('s3')
    s3_bucket_name = s3_bucket_name or f'babysage-{aws_account_id}-{region_name}'

    try:
        s3.get_bucket_location(Bucket=s3_bucket_name)
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            # bucket doesn't exist
            print(f'S3 bucket {s3_bucket_name} doesn\'t seem to be exist')
            if input('Can I create one? [y/N]') in 'yY':
                s3.create_bucket(
                    Bucket=s3_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region_name})

    '''
    iam = session.client('iam')
    try:
        iam.get_bucket_location(Bucket=s3_bucket_name)
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            # bucket doesn't exist
            click.echo(f'S3 bucket {s3_bucket_name} doesn\'t seem to be exist')
            if input('Can I create one? [Y/n]') in 'yY ':
                s3.create_bucket(
                    Bucket=s3_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region_name})
    '''

    template_dir = 'templates/default'

    ctx = {
        'babysage':
            {
                'experiment_name': name,
                'ecr_repo_name': ecr_repo_name,
                's3_bucket_name': s3_bucket_name}}

    for t in _expand_template(template_dir):
        out_path = Template(os.path.join(t[len(template_dir) + 1:])).render(ctx)
        if not os.path.isdir(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        with open(pkg_resources.resource_filename('babysage', t), 'r') as f_in:
            with open(out_path, 'w') as f_out:
                f_out.write(
                    Template(f_in.read()).render(ctx))
                if os.path.basename(out_path) == 'train':
                    import stat
                    os.chmod(out_path, stat.S_IEXEC)


def _expand_template(root):
    if pkg_resources.resource_isdir('babysage', root):
        resources = []
        for r in pkg_resources.resource_listdir('babysage', root):
            resources += _expand_template(os.path.join(root, r))
        return resources
    else:
        if pkg_resources.resource_exists('babysage', root):
            return [root]
        else:
            raise Exception(f'Couldn\'t find the resource {root} on package `babysage`')
