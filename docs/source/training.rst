Training
++++++++++++

Processing jobs accept a set of one or more input file paths and write to a set of one or more output file paths. Ideal for file conversion or other data preparation tasks.


* Running locally, standard command line arguments for inputs and outputs are used as usual
* Running remotely, data is uploaded and downloaded using S3 for tracking

Basic usage
-----------

Write a script with a ``main`` function that calls ``sagemaker_training_main``.

.. code-block:: python

   from aws_sagemaker_remote import sagemaker_training_main

   def main(args):
       # your code here
       pass

   if __name__ == '__main__':
       sagemaker_training_main(
           main=main,
           # ...
       )

Pass function argument ``run=True`` or command line argument ``--sagemaker-run=True`` to run script remotely on SageMaker.

* Many command-line arguments are automatically added. See :ref:`Training Command-Line Arguments`.
* Parameters to ``sagemaker_processing_main`` control what command-line arguments are automatically added
  and the default values. See :meth:`aws_sagemaker_remote.training.main.sagemaker_training_main` and
  :meth:`aws_sagemaker_remote.training.args.sagemaker_training_args`

Training Job Tracking
-----------------------

Use the SageMaker console to view a list of all training jobs. For each job, SageMaker tracks:


* Training time
* Container used
* Link to CloudWatch logs
* Path on S3 for each of:

  * Source code ZIP
  * Each input channel
  * Model output ZIP
  * Dependencies (if used)

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

  * Function argument ``training_instance``
  * Command line argument ``--sagemaker-training-instance``
  * Select instance type of machine running the container

* Image

  * Function argument ``training_image``
  * Command line argument ``--sagemaker-training-image``
  * Accepts URI of Docker container image on ECR or DockerHub to run
  * Build a custom Docker image for major customizations

* Requirements file

  * Create a file named ``requirements.txt`` in your ``source`` directory
  * ``source`` directory defaults to the directory containing your script but can be overridden
  * Use for installing Python packages by listing one on each line. Standard ``requirements.txt`` file format [https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format]

* Dependencies

  * Function argument ``dependencies``

    * Dictionary of ``[key]->[value]``
    * Each key will create command line argument ``--key`` that defaults to ``value``

  * Each ``value`` is a directory containing a Python module that will be uploaded to S3, downloaded to SageMaker, and put on the PYTHONPATH
  * For example, if directory ``mymodule`` contains the files ``__init__.py`` and ``myfile.py`` and ``myfile.py`` contains ``def myfunction():...``\ , pass ``dependencies={'mymodule':'path/to/mymodule'}`` to ``sagemaker_processing_main`` and then use ``from mymodule.myfile import myfunction`` in your script.
  * Use module uploads for supporting code that is not being installed from packages.

Additional arguments
--------------------

Any arguments passed to your script locally on the command line are passed to your script remotely and tracked by SageMaker. Internally, ``sagemaker_processing_main`` uses ``argparse``. To add additional command-line flags:


* Pass a list of kwargs dictionaries to  ``additional_arguments``

  .. code-block:: python

    sagemaker_training_main(
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
    sagemaker_training_main(
      # ...
      argparse_callback=argparse_callback
    )

.. _Training Command-Line Arguments:

Command-Line Arguments
----------------------

.. argparse::
   :module: aws_sagemaker_remote.training.args
   :func: sagemaker_training_parser_for_docs
   :prog: aws-sagemaker-remote-training
        
