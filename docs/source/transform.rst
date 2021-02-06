SageMaker Batch Transform
=========================

SageMaker Batch Transform creates a fleet of containers to run parallel processing
on objects in S3. Batch Transform is best used when 
you need a custom image or to load large objects into memory (e.g., batch machine learning).

- If the process is not parallel across files, use SageMaker processing, which will 
  allocate a machine and make S3 files available locally for python processing
  :ref:`SageMaker Processing documentation<processing:SageMaker Processing>`
- If the process can be run in a small JavaScript package, processing can be performed
  faster, cheaper, and with better parallelization using S3 batch.
  :ref:`S3 Batch documentation<batch:S3 Batch Processing>`

Usage
-------------

Create a SageMaker model, which consists of:

- GZip file containing code
- ECR docker image URI

You can create a model:

- Automatically as the output of any ``aws-sagemaker-remote`` training job
- Manually by uploading a GZip containing your code, building an ECR image, and running ``aws-sagemaker-remote model create``

You can create a fleet of containers running your model from the command line.

- You define the number of instancs and the type of instance
- Each file is posted to your model using the Accept (output) and Content-Type (input) MIME types you specify
- Each response from your model is saved to S3 with the extension ``.out``

Command-Line Interface
-----------------------

The command ``aws-sagemaker-remote transform create`` will start a job.

Run ``aws-sagemaker-remote transform create --help`` for help.

.. click:: aws_sagemaker_remote.cli:cli
   :prog: aws-sagemaker-remote
   :nested: full
   :commands: transform

See `CLI documentation <cli.html#aws-sagemaker-remote-transform-create>`_.