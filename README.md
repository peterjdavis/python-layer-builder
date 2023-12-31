# Overview
When authoring a Lambda function it may require dependencies which require building and deploying with the function or as a layer.  This Serverless Application uses Lambda to build a Lambda Layer containing your dependencies removing the need for you to package them locally and upload them.

To prevent multiple Lambdas being created in accounts, I've created multiple version of the application for different python runtimes and architectures:
* python3-11-arm64-layer-builder - python3.11 arm64
* python3-11-x86-64-layer-builder - python3.11 x86_64
* python3-10-arm64-layer-builder - python3.10 arm64
* python3-10-x86-64-layer-builder - python3.10 x86_64

# Instructions

### Console Deployment
The Serverless Application can be installed using the console using the [Serverless Application Repository](https://console.aws.amazon.com/serverlessrepo/home#/available-applications).
1. On the 'Public Applications' tab search for "layer-builder" (make sure you have the 'Show apps that create custom IAM roles or resource policies' tick box ticked) and then click on the application
1. In the Lambda page that is opened under the 'Application Settings' section provide a name for the Layer that will be created and list the packages that you would like to be included in your layer (using the same format as [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing). Make sure the 'I acknowledge that this app creates custom IAM roles.' tick box is ticked
1. Click 'Deploy'
1. You check progress of the deployment under the 'Deployment' tab of the window that is opened
1. Once the deployment has finished you will be able to see the created Lambda Layer under the [Layers](https://console.aws.amazon.com/lambda/home?#/layers) section of the Lambda Console

### SAM Deployment
To include the Serverless Application in your own SAM template.
1. On the 'Public Applications' tab search for "layer-builder" (make sure you have the 'Show apps that create custom IAM roles or resource policies' tick box ticked) and then click on the application
1. Click the 'Copy as Sam Resource' button in the top right of the page
1. Paste the code into your SAM template
1. Populate the two parameters:
    * LayerName - the name of the Lambda Layer that will be generated 
    * LayerPackages - the packages that you would like to be included in your layer (using the same format as [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing)
1. Make sure when you deploy your SAM template the parameter ```--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM``` is passed to the SAM CLI

### Sample 
In the [samples](https://github.com/peterjdavis/python-layer-builder/tree/main/samples) folder is an example SAM and CloudFormation template which shows deploying the Serverless Application and using the generated Lambda Layer in a Lambda Function.  **Note** the CloudFormation template still requires the transform for the AWS::ServerlessRepo::Application resource as there are no permissions for CloudFormation to access the resources outside of the Serverless Application Repository i.e. using a nested stack.

# Reporting Issues
Please report any issues you find using in the [GitHub repository issue tracker](https://github.com/peterjdavis/python-layer-builder/issues) 
      