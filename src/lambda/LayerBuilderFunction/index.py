import cfnresponse
import os
import shutil
import boto3
import logging

LAYER_NAME = os.environ['LAYER_NAME']
LAYER_PACKAGES = os.environ['LAYER_PACKAGES']
PYTHON_VERSION = os.environ['PYTHON_VERSION']
ARCHITECTURE = os.environ['ARCHITECTURE']
TEMP_S3_BUCKET_NAME=os.environ['TEMP_S3_BUCKET_NAME']
AWS_REGION=os.environ['AWS_REGION']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    responseData = {}
    if event['RequestType'] == 'Delete':
        try:
            delete_layer()
            responseData = {'success': 'true'}
        except Exception as e:
            responseData = {'error': str(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
            return
    if event['RequestType'] == 'Create':
        try:
            layer_version_arn = build_layer()
            responseData['LayerVersionArn'] = layer_version_arn
        except Exception as e:
            responseData = {'error': str(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
            return
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)

def build_layer():
    os.system(f'cd /tmp; python -m venv {LAYER_NAME}/python; source {LAYER_NAME}/python/bin/activate; python -m pip install {LAYER_PACKAGES}')
    shutil.make_archive(f'/tmp/{LAYER_NAME}', 'zip', f'/tmp/{LAYER_NAME}')

    # Get the size of the zipped file
    zip_stats = os.stat(f'/tmp/{LAYER_NAME}.zip')
    zip_size = zip_stats.st_size / (1024 * 1024)

    if zip_size >= 50:
        logger.info(f'Creating Layer via S3 as zip size is {zip_size} MB bucket name is {TEMP_S3_BUCKET_NAME}')
        s3_client.create_bucket(Bucket=TEMP_S3_BUCKET_NAME,
                                CreateBucketConfiguration={'LocationConstraint': AWS_REGION})
        s3_client.upload_file(f'/tmp/{LAYER_NAME}.zip', TEMP_S3_BUCKET_NAME, f'{LAYER_NAME}.zip')
        response = lambda_client.publish_layer_version(
            LayerName=LAYER_NAME,
            Content={
                'S3Bucket': TEMP_S3_BUCKET_NAME,
                'S3Key': f'{LAYER_NAME}.zip'
            },
            CompatibleRuntimes=[
                PYTHON_VERSION
            ],
            CompatibleArchitectures=[
                ARCHITECTURE,
            ]
        )
        logger.info(f'Cleaning up S3 Bucket {TEMP_S3_BUCKET_NAME}')
        s3_client.delete_object(Bucket=TEMP_S3_BUCKET_NAME, Key=f'{LAYER_NAME}.zip')
        s3_client.delete_bucket(Bucket=TEMP_S3_BUCKET_NAME)
    else:
        logger.info(f'Creating Layer directly as zip size is {zip_size} MB')
        with open(f'/tmp/{LAYER_NAME}.zip', 'rb') as layer_zip:
            response = lambda_client.publish_layer_version(
                LayerName=LAYER_NAME,
                Content={
                    'ZipFile': layer_zip.read()
                },
                CompatibleRuntimes=[
                    PYTHON_VERSION
                ],
                CompatibleArchitectures=[
                    ARCHITECTURE,
                ]
            )
    return (response['LayerVersionArn'])

def delete_layer():
    response = lambda_client.list_layer_versions(
        LayerName=LAYER_NAME
    )

    for layer_version in response['LayerVersions']:
        logger.info(f'Deleting layer version {layer_version["Version"]}')
        response = lambda_client.delete_layer_version(
            LayerName=LAYER_NAME,
            VersionNumber=layer_version['Version']
        )
        logger.info(f'Delete response: {response}')
