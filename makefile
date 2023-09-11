SHELL := /bin/bash
.ONESHELL:

ENV ?= dummy
-include envs/${ENV}
export

.PHONY : init
init : 
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -U pip
	pip3 install -r requirements.txt

.PHONY : update-variables
update-variables : 
	$(eval tmpDir := $(shell mktemp -d))

	sed 's/%python-version-desc%/${python-version-desc}/g' template.yaml > ${tmpDir}/template.yaml
	sed -i '' 's/%architecture%/${architecture}/g' ${tmpDir}/template.yaml
	sed -i '' 's/%layer-label%/${layer-label}/g' ${tmpDir}/template.yaml

	cp ${tmpDir}/template.yaml template-processed.yaml
	rm -rf ${tmpDir}

.PHONY : package
package : update-variables
	sam build --template template-processed.yaml
	sam package --output-template-file packaged.yaml \
				--s3-bucket python-layer-builder
	rm template-processed.yaml

.PHONY : publish
publish : package
	sam publish --template packaged.yaml --region eu-west-1
	rm packaged.yaml 

publish-all : envs/*
	@for file in $^ ; do \
		make publish ENV=`echo $${file} | sed 's/envs\///'` ; \
	done

.PHONY : deploy-sam-sample
deploy-sam-sample :
	sam deploy --template samples/requests-layer-template-sam.yaml \
			   --stack-name requests-layer-sam \
			   --resolve-s3 \
			   --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM

.PHONY : deploy-cfn-sample
deploy-cfn-sample :
	aws cloudformation deploy --template-file samples/requests-layer-template-cfn.yaml \
						      --stack-name requests-layer-cfn \
							  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

.PHONY : delete-sam-sample
delete-sam-sample :
	sam delete --stack-name requests-layer-sam --no-prompts

.PHONY : delete-cfn-sample
delete-cfn-sample :
	aws cloudformation delete-stack --stack-name requests-layer-cfn