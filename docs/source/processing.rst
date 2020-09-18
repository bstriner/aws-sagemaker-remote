Processing
===========

Processing jobs accept a set of one or more input file paths and write to a set of one or more output file paths. Ideal for file conversion or other data preparation tasks.


* Running locally, standard command line arguments for inputs and outputs are used as usual
* Running remotely, data is uploaded and downloaded using S3 for tracking

Basic usage
-----------

Write a script with a ``main`` function that calls ``sagemaker_processing_main``.

.. code-block:: python

   from aws_sagemaker_remote.processing import sagemaker_processing_main

   def main(args):
       # your code here
       pass

   if __name__ == '__main__':
       sagemaker_processing_main(
           script=__file__,
           main=main,
           # ...
       )

Pass function argument ``run=True`` or command line argument ``--sagemaker-run=True`` to run script remotely on SageMaker.

Processing Job Tracking
-----------------------

Use the SageMaker console to view a list of all processing jobs. For each job, SageMaker tracks:


* Processing time
* Container used
* Link to CloudWatch logs
* Path on S3 for each of:

  * Script file
  * Each input channel
  * Each output channel
  * Requirements file (if used)
  * Configuration script (if used)
  * Supporting code (if used)

Configuration
-------------

Many command line options are added by this command.

Option ``--sagemaker-run`` controls local or remote execution.


* Set ``--sagemaker-run`` to a falsy value (no,false,0), the script will call your main function as usual and run locally. 
* Set ``--sagemaker-run`` to a truthy value (yes,true,1), the script will upload itself and any requirements or inputs to S3, execute remotely on SageMaker, and save outputs to S3, logging results to the terminal.

Set ``--sagemaker-wait`` truthy to tail logs and wait for completion or falsy to complete when the job starts.

Defaults are set through code. Defaults can be overwritten on the command line. For example:


* Use the function argument ``image`` to set the default container image for your script
* Use the command line argument ``--sagemaker-image`` to override the container image on a particular run

See **functions** and **commands** (todo: links)

Environment Customization
-------------------------

The environment can be customized in multiple ways.


* Instance

  * Function argument ``instance``
  * Command line argument ``--sagemaker-instance``
  * Select instance type of machine running the container

* Image

  * Function argument ``image``
  * Command line argument ``--sagemaker-image``
  * Accepts URI of Docker container image on ECR to run
  * Build a custom Docker image for major customizations

* Configuration script

  * Function argument ``configuration_script``
  * Command line argument ``--sagemaker-configuration-script``
  * Accepts path to a text file. Will upload text file to S3 and run ``source [file]``.
  * Batch script for minor customization, e.g., ``export MYVAR=value`` or ``yum install -y mypackage``

* Requirements file

  * Function argument ``requirements``
  * Command line argument ``--sagemaker-requirements``
  * Accepts path to a text file. Will upload text file to S3 and run ``python -m pip install -r [file]``
  * Use for installing Python packages by listing one on each line. Standard ``requirements.txt`` file format [https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format]

* Module uploads

  * Function argument ``modules``

    * Dictionary of ``[key]->[value]``
    * Each key will create command line argument ``--key`` that defaults to ``value``

  * Each ``value`` is a directory containing a Python module that will be uploaded to S3, downloaded to SageMaker, and put on the PYTHONPATH
  * For example, if directory ``mymodule`` contains the files ``__init__.py`` and ``myfile.py`` and ``myfile.py`` contains ``def myfunction():...``\ , pass ``modules={'mymodule':'path/to/mymodule'}`` to ``sagemaker_processing_main`` and then use ``from mymodule.myfile import myfunction`` in your script.
  * Use module uploads for supporting code that is not being installed from packages.

Additional arguments
--------------------

Any arguments passed to your script locally on the command line are passed to your script remotely and tracked by SageMaker. Internally, ``sagemaker_processing_main`` uses ``argparse``. To add additional command-line flags:


* Pass a list of kwargs dictionaries to  ``additional_arguments``

  .. code-block:: python

    sagemaker_processing_main(
      #...
      additional_arguments = [
        {
          'dest': '--filter-width',
          'default':32,
          'help':'Filter width'
        },
        {
          'dest':'--filter-height',
          'default':32,
          'help':'Filter height'
        }
      ]
    )

* Pass a callback to ``argparse_callback``

  .. code-block:: python

    from argparse import ArgumentParser
    def argparse_callback(parser:ArgumentParser):
      parser.add_argument(
      '--filter-width',
      default=32,
      help='Filter width')
      parser.add_argument(
      '--filter-height',
      default=32,
      help='Filter height')



Command-Line Arguments
----------------------

.. argparse::
   :module: aws_sagemaker_remote.processing.args
   :func: sagemaker_processing_parser_for_docs
   :prog: aws-sagemaker-remote-processing

    --output
        An output flag will be generated for each item in the :code:`outputs` parameter to :code:`sagemaker_processing_main`
        
    --input
        An input flag will be generated for each item in the :code:`input` parameter to :code:`sagemaker_processing_main`

        
