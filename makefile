SHELL := /bin/bash
.ONESHELL:

.PHONY : init
init : 
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -U pip
	pip3 install -r requirements.txt

.PHONY : package
package : 
	sam build
	sam package --output-template-file packaged.yaml --s3-bucket python-layer-builder

.PHONY : publish
publish : package
	sam publish --template packaged.yaml --region eu-west-1

.PHONY : deploy-sample
deploy-sample :
	sam deploy --template samples/requests-layer-template.yaml \
			   --stack-name requests-layer-4 \
			   --resolve-s3 \
			   --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM

.PHONY : delete-sample
delete-sample :
	sam delete --stack-name requests-layer-4 --no-prompts