import os
import boto3
import click
import pkg_resources

from jinja2 import Template

from babysage.config import get_config


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@main.command()  # @cli, not @click!
@click.option('--name', nargs=1, type=str, required=True)
@click.option('--ecr-repo-name', '-r', 'ecr_repo_name', nargs=1, type=str)
@click.option('--s3-bucket-name', '-b', 's3_bucket_name', nargs=1, type=str)
@click.option('--region', '-r', 'region', nargs=1, type=str)
def init(name, ecr_repo_name, s3_bucket_name, region):
    click.echo(f'Creating babysage experiment {name}.')

    region_name = region or boto3.session.Session().region_name
    ecr = boto3.client('ecr')
    ecr_repo_name = ecr_repo_name or f'babysage-{name}'

    try:
        resp = ecr.describe_repositories(repositoryNames=[ecr_repo_name])
        ecr_repo_arn = resp['repositories'][0]['repositoryArn']
    except Exception as e:
        print(e.__dict__)
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            click.echo(f'ECR repositroy {ecr_repo_name} doesn\'t seem to be exist')
            if input('Can I create one? [Y/n]') in 'yY ':
                print('create')
                pass
                # resp = ecr.create_repository(repositoryName=ecr_repo_name)
                # ecr_repo_arn = resp['repository']['repositoryArn']
                ecr_repo_arn = 'dummy'
            else:
                print('not create')
                ecr_repo_arn = '$ECR_REPO_ARN$'
                pass

    s3 = boto3.client('s3')
    s3_bucket_name = s3_bucket_name or f'babysage-{region_name}'

    try:
        s3.get_bucket_location(Bucket=s3_bucket_name)
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            # bucket doesn't exist
            click.echo(f'S3 bucket {s3_bucket_name} doesn\'t seem to be exist')
            if input('Can I create one? [Y/n]') in 'yY ':
                print('create')
                pass
                # s3.create_bucket(Bucket=s3_bucket_name)
            else:
                print('not create')
                pass

    template_dir = 'templates/default'

    ctx = {
        'babysage':
            {
                'experiment_name': name,
                'ecr_repo_arn': ecr_repo_arn,
                's3_bucket_name': s3_bucket_name}}

    for t in _expand_template(template_dir):
        out_path = Template(os.path.join(t[len(template_dir) + 1:])).render(ctx)
        if not os.path.isdir(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        with open(pkg_resources.resource_filename('babysage', t), 'r') as f_in:
            with open(out_path, 'w') as f_out:
                f_out.write(
                    Template(f_in.read()).render(ctx))


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


@main.command()
def run_local():
    click.echo('まだだよ')


@main.command()
def run_remote():
    training_params = {
        "AlgorithmSpecification": {
            "TrainingImage": '873096238884.dkr.ecr.us-west-2.amazonaws.com/konpeki/ml-car:00300_initial_experiment',
            "TrainingInputMode": "File"
        },
        "RoleArn": 'arn:aws:iam::873096238884:role/service-role/AmazonSageMaker-ExecutionRole-20180516T165044',
        "OutputDataConfig": {
            "S3OutputPath": 's3://aibs-oregon-ml-test-data/ml-car/output/00300_initial_experiment/'
        },
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": "ml.p3.2xlarge",
            "VolumeSizeInGB": 300
        },
        "TrainingJobName": job_name,
        # "HyperParameters": {
        #   "top_k": str(top_k),
        # },
        "InputDataConfig": [
            {
                "ChannelName": "main",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": 's3://aibs-oregon-ml-test-data/ml-car/data/00300_initial_experiment/',
                        "S3DataDistributionType": "FullyReplicated"
                    }
                },
                "ContentType": "application/x-image",
                "CompressionType": "None"
            }
        ],
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 360000
        },
    }


@main.command()
def data_up():
    click.echo('まだだよ')


@main.command()
def data_down():
    click.echo('まだだよ')


@main.command()
@main.argument('hash_hint')
def logs(hash_hint):
    click.echo('まだだよ')
    click.echo(hash_hint)


# resource_stream(package_or_requirement, resource_name)
# resource_string(package_or_requirement, resource_name)
