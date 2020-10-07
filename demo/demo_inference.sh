
   aws-sagemaker-remote upload demo/demo_model demo-model/model.tar.gz --gz
   aws-sagemaker-remote model create --name demo-model --model-artifact demo-model/model.tar.gz --force
   aws-sagemaker-remote endpoint-config create --model demo-model --force
   aws-sagemaker-remote endpoint create --config demo-model --force
   aws sagemaker wait endpoint-in-service --endpoint-name demo-model
   aws-sagemaker-remote endpoint invoke demo-model --input demo/test_image.jpg --output output/result/result_image.jpg --output-type image/jpeg
   aws-sagemaker-remote endpoint delete demo-model
   aws-sagemaker-remote endpoint-config delete demo-model
   aws-sagemaker-remote model delete demo-model
   md5sum demo/test_image.jpg
   md5sum output/result/result_image.jpg
   
   