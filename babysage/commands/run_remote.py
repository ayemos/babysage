from babysage.config import get_config

def run_remote():
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    job_name = get_config('experiment_name') + '-' + timestamp
    session = boto3.session.Session()

    aws_account_id = boto3.client('sts').get_caller_identity()['Account']
    region_name = session.region_name
    ecr_repo_arn = f"{aws_account_id}.dkr.ecr.{region_name}.amazonaws.com/{get_config('ecr_repo_name')}"

    training_params = {
        "AlgorithmSpecification": {
            "TrainingImage": os.path.join(
                get_config('ecr_repo_name'), get_config('experiment_name')),
            "TrainingInputMode": "File"
        },
        "RoleArn": get_config('execution_role_arn'),
        "OutputDataConfig": {
            "S3OutputPath": f"s3://{get_config('s3_bucket_name')}/{get_config('experiment_name')}/output/{job_name}"
        },
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": get_config('instance_type'),
            "VolumeSizeInGB": get_config('volume_size_in_gb'),
        },
        "TrainingJobName": job_name,
        "InputDataConfig": [
            {
                "ChannelName": "main",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{get_config('s3_bucket_name')}/{get_config('experiment_name')}/input/",
                        "S3DataDistributionType": "FullyReplicated"
                    }
                },
            }
        ],
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 360000
        },
        'Tags': [
            {
                'Key': 'babysage-experiment-name',
                'Value': get_config('experiment_name')}],
    }

    sagemaker = boto3.client(service_name='sagemaker')
    sagemaker.create_training_job(**training_params)

    # confirm that the training job has started
    status = sagemaker.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
    print('Training job current status: {}'.format(status))

    try:
        # wait for the job to finish and report the ending status
        sagemaker.get_waiter('training_job_completed_or_stopped').wait(TrainingJobName=job_name)
        training_info = sagemaker.describe_training_job(TrainingJobName=job_name)
        status = training_info['TrainingJobStatus']
        print("Training job ended with status: " + status)
    except Exception as e:
        print('Training failed to start')
        print('Exception', e)
        # if exception is raised, that means it has failed
        message = sagemaker.describe_training_job(TrainingJobName=job_name)['FailureReason']
        print('Training failed with the following error: {}'.format(message))

