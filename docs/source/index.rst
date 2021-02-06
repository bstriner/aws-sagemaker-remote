.. aws-sagemaker-remote documentation master file, created by
   sphinx-quickstart on Thu Sep 17 18:38:43 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Simplify AWS usage with aws-sagemaker-remote
================================================

Library and command-line for performing processing using AWS 
with minimal configuration and AWS knowledge required.

- :ref:`SageMaker Training<training:SageMaker Training>` to remotely run training scripts,
  automatically managing required resources and enabling a host of command-line options
- :ref:`SageMaker Processing<processing:SageMaker Processing>` to remotely
  run python processing scripts using S3 data with little modification required
- :ref:`SageMaker Batch Transform<transform:SageMaker Batch Transform>` to run
  parallel processing of objects in S3 on SageMaker containers
- :ref:`S3 Batch Processing<batch:S3 Batch Processing>` to run massively
  parallel processing of objects in S3 using Lambda functions
- :ref:`SageMaker Inference<inference:SageMaker Inference>` to deploy 
  models for real-time inference
- :ref:`Command-Line Interface<cli:Command-Line Interface>` containing utilities
  for managing AWS resources

.. toctree::
   :maxdepth: 2
   :caption: Contents

   README <readme>
   cli
   processing
   batch
   transform
   training
   inference
   Modules <modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
