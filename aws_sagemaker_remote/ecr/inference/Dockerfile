#
#
# `aws ecr get-login --no-include-email --registry-ids 763104351884`
# `aws ecr get-login --no-include-email`
#  
# docker build . -t columbo:inference-cpu-0.0.1 && docker tag columbo:inference-cpu-0.0.1 683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo:inference-cpu-0.0.1 && docker push 683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo:inference-cpu-0.0.1 &
# docker run -it columbo:inference-cpu-0.0.1  bash
ARG REGION=us-east-1
FROM 763104351884.dkr.ecr.${REGION}.amazonaws.com/pytorch-inference:1.5.1-cpu-py36-ubuntu16.04
RUN apt-get update && apt-get install -y libsvm3 sox
RUN pip install --no-cache-dir --upgrade pandas awscli boto3 multi-model-server sagemaker-inference==1.5.1 sagemaker-pytorch-inference==1.5.1 sagemaker pytorch-igniter scipy torch torchvision matplotlib pillow
RUN pip install --no-cache-dir --upgrade torchaudio
RUN pip install --no-cache-dir --upgrade webrtcvad

RUN python -c "import torchaudio"
