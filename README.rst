
aws-sagemaker-remote
++++++++++++++++++++

Remotely run and track ML research using AWS SageMaker.


* Standardized command line flags
* Remotely run scripts with minimal changes
* Automatically manage AWS resources
* All code, inputs, outputs, arguments, and settings are tracked in one place
* Reproducible batch processing jobs to prepare datasets
* Reproducible training jobs that track hyperparameters and metrics

Track three types of objects in a standard way:

* Processing jobs consume file inputs and produce file outputs. Useful for data conversion, extraction, etc.
* Training jobs train models while tracking metrics and hyperparameters.
* Inference models provide predictions and can be deployed on endpoints. Can be automatically created from and linked to training jobs for tracking purposes or can deploy externally-created models.


Installation
=======================

Release
-------

.. code-block:: bash

   pip install aws-sagemaker-remote

Development
-----------

.. code-block:: bash

   git clone https://github.com/bstriner/aws-sagemaker-remote
   cd aws-sagemaker-remote
   python setup.py develop

Documentation
=======================

View latest documentation at `ReadTheDocs <https://aws-sagemaker-remote.readthedocs.io/>`_

Continuous Integration
=======================

View continuous integration at `TravisCI <https://travis-ci.org/github/bstriner/aws-sagemaker-remote>`_


PyPI
=======================

View releases on `PyPI <https://pypi.org/project/aws-sagemaker-remote/>`_


GitHub
=======================

View source code on `GitHub <https://github.com/bstriner/aws-sagemaker-remote>`_

GitHub tags are automatically released on ReadTheDocs, tested on TravisCI, and deployed to PyPI if successful.

