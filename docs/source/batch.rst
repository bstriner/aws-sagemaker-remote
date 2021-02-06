S3 Batch Processing
===================

S3 batch processing is best used when you need to run a massively parallel process
across files in S3 and you can pack your processing code into a small size for Lambda.

- If the process is not parallel across files, use SageMaker processing, which will 
  allocate a machine and make S3 files available locally for python processing
  :ref:`SageMaker processing documentation<processing:SageMaker Processing>`
- If the process requires more code or a custom image that cannot be used by a Lambda,
  but the process can be fully parallelized,
  use SageMaker batch processing to allocate a fleet of containers that will process each
  object in S3.
  :ref:`SageMaker transform documentation<transform:SageMaker Batch Transform>`

Usage
---------

There are two steps to writing a process for S3 Batch:

- Write a Lambda function that performs the parallel processing
- Write a python wrapper that configures deploying the function and any arguments

Lambda
+++++++

Write a Lambda function.

- Create a folder containing your Lambda function
- ``package.json`` containing dependencies
- ``index.js`` exporting a function named ``handler``
- See required input and output format in `AWS S3 Batch documentation <https://docs.aws.amazon.com/lambda/latest/dg/services-s3-batch.html>`_
- You may use import statements and packages, the function will be automatically webpacked

.. literalinclude:: ../../demo/demo_batch/lambda/index.js
  :language: JavaScript

Python
+++++++

Write a Python wrapper referencing the folder containing your Lambda to generate a CLI.
Running this wrapper will:

- Create roles and permissions (if necessary)
- Build and deploy the Lambda (if necessary)
- Tag a version of the Lambda with environment arguments specified by the command line
- Create a batch processing job in S3 using that Lambda tag
- Optionally confirm the job, otherwise it can be confirmed in the AWS S3 console
- Optionally save Job ID in a JSON file for later reference

.. literalinclude:: ../../demo/demo_batch/demo_batch.py
  :language: python


Command-Line Interface
------------------------

The above code generates the following command line interface which can be used to 
build, deploy, and run the batch job.

.. argparse::
   :module: demo_batch.demo_batch_parser
   :func: parser
   :prog: demo-batch

