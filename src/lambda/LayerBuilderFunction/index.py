import cfnresponse
import os
import shutil
import boto3
import logging

LAYER_NAME = os.environ['LAYER_NAME']
LAYER_PACKAGES = os.environ['LAYER_PACKAGES']
PYTHON_VERSION = os.environ['PYTHON_VERSION']
ARCHITECTURE = os.environ['ARCHITECTURE']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client('lambda')

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
