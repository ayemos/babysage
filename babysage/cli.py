import click


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    pass


@main.command()  # @cli, not @click!
@click.option('--name', nargs=1, type=str, required=True)
@click.option('--ecr-repo-name', '-r', 'ecr_repo_name', nargs=1, type=str)
@click.option('--s3-bucket-name', '-b', 's3_bucket_name', nargs=1, type=str)
@click.option('--execution-role-arn', '-e', 'execution_role_arn', nargs=1, type=str)
@click.option('--region', '-r', 'region', nargs=1, type=str)
def init(
        name,
        ecr_repo_name,
        s3_bucket_name,
        execution_role_arn,
        region):
    from babysage.commands.init import init
    init(
        name,
        ecr_repo_name,
        s3_bucket_name,
        execution_role_arn,
        region)


@main.command()
@click.option('--docker-file', '-f', 'dockerfile', nargs=1, type=str, default=None)
def run_local(dockerfile):
    from babysage.commands.run_local import run_local
    run_local(dockerfile)


@main.command()
@click.option('--docker-file', '-f', 'dockerfile', nargs=1, type=str, default=None)
def deploy(dockerfile):
    from babysage.commands.deploy import deploy
    deploy(dockerfile)


@main.command()
def run_remote():
    from babysage.commands.run_remote import run_remote
    run_remote()


@main.command()
def data_up():
    click.echo('まだだよ')


@main.command()
def data_down():
    click.echo('まだだよ')


@main.command()
@click.argument('hash_hint')
def logs(hash_hint):
    click.echo('まだだよ')
    click.echo(hash_hint)
