SageMaker Inference
============================

SageMaker real-time inference deploys your models to containers 
so they are always ready to perform inference quickly.

Terminology
------------

- An inference package is a GZip file.

  - The root of this package is the ``model_dir``
  - The package must contain a folder named ``code`` containing a file named ``inference.py``

- A SageMaker model identifies an inference package and an ECR docker image
- A SageMaker endpoint configuration describes a set of models and the type and number of instances
- A SageMaker endpoint is a deployment of an endpoint configuration that is live for inference

Usage
------------

Create a model

- Automatically as the output of an ``aws-sagemaker-remote`` training script
- Manually by uploading a GZip file to S3 and building a docker image

Invoke a local inference package extracted to a folder

.. code-block: bash

   aws-sagemaker-remote endpoint invoke --model-dir demo/demo_model --input demo/test_image.jpg --output output/result/local_result.jpg --output-type image/jpeg
   md5sum demo/test_image.jpg
   md5sum output/result/local_result.jpg

Create, invoke, then destroy a remote endpoint

.. code-block: bash

   aws-sagemaker-remote upload demo/demo_model demo-model/model.tar.gz --gz
   aws-sagemaker-remote model create --name demo-model --model-artifact demo-model/model.tar.gz --force
   aws-sagemaker-remote endpoint-config create --model demo-model --force
   aws-sagemaker-remote endpoint create --config demo-model --force
   aws sagemaker wait endpoint-in-service --endpoint-name demo-model
   aws-sagemaker-remote endpoint invoke --name demo-model --input demo/test_image.jpg --output output/result/sagemaker_result.jpg --output-type image/jpeg
   aws-sagemaker-remote endpoint delete demo-model
   aws-sagemaker-remote endpoint-config delete demo-model
   aws-sagemaker-remote model delete demo-model
   md5sum demo/test_image.jpg
   md5sum output/result/result_image.jpg
   
Build docker images for models

.. code-block: bash

   aws-sagemaker-remote ecr build aws-sagemaker-remote-inference:latest

