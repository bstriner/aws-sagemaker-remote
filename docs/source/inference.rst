Inference
=========

.. code-block: bash

   aws-sagemaker-remote endpoint invoke --model-dir demo/demo_model --input demo/test_image.jpg --output output/result/local_result.jpg --output-type image/jpeg
   md5sum demo/test_image.jpg
   md5sum output/result/local_result.jpg


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
   
   