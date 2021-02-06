Command-Line Interface
=======================

The ``aws-sagemaker-remote`` CLI provides utilities to compliment
processing, training, and other scripts.

Most inputs to these utilities are actually CSV strings that are processed left-to-right.

- For most use-cases, pass the raw string. If the string includes a comma, it should be double-quoted.
- For more advanced use-cases, pass a CSV string of operations

  - Start with a string value
  - Pass ``sagemaker`` to interpret the current string as a relative path in the default SageMaker bucket
  - Pass ``json:key`` to interpret the current string as a local or s3 path, read that file, and get a JSON key from that file
  - Pass ``processing:key`` to interpret the current string as a processing job ID and get a value from that job
  - Pass ``training:key`` to interpret the current string as a training job ID and get a value from that job
  - Pass ``batch:key`` to interpret the current string as an S3 batch job ID and get a value from that job

For example, when specifying the input to a script on the command line:

- For known path, simply pass the value, ``--input s3://bucket/relative/path``
- Instead of hardcoding your default SageMaker bucket, use ``--input relative/path,sagemaker``
- For referencing a key named ``mykey`` in a JSON, use ``--input file.json,json:mykey``
- For a more complicated example, like referencing the output of a processing job:

  - When running a processing job use ``--output-json relative/path.json`` to save the JobID to JSON
  - Reference the job output by specifying ``--input relative/path.json,json:JobId,processing:ProcessingOutputConfig.Outputs.outputname.S3Output.S3Uri``

.. click:: aws_sagemaker_remote.cli:cli
   :prog: aws-sagemaker-remote
   :nested: full