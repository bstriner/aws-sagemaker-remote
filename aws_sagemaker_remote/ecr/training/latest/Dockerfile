# aws-sagemaker-remote ecr build training-gpu
#
# `aws ecr get-login --no-include-email --registry-ids 763104351884`
# `aws ecr get-login --no-include-email`
#  
# docker build . -t columbo:training-cpu-0.0.1 && docker tag columbo:training-cpu-0.0.1 683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo:training-cpu-0.0.1 && docker push 683880991063.dkr.ecr.us-east-1.amazonaws.com/columbo:training-cpu-0.0.1 &
# docker run -it columbo:training-cpu-0.0.1  bash
ARG REGION=us-east-1

FROM 763104351884.dkr.ecr.${REGION}.amazonaws.com/pytorch-training:1.6.0-cpu-py36-ubuntu16.04
# FROM nvidia/cuda:11.1-cudnn8-runtime-ubuntu18.04
# https://github.com/aws/deep-learning-containers/blob/master/available_images.md
RUN apt-get update && \
  apt-get install -y libsvm3 sox libsox-dev
#RUN conda install -y -c mlio -c conda-forge mlio-py libmlio 
#libmlio-devel libmlio-dbg
#RUN conda install -y -c pytorch pytorch torchvision torchaudio
RUN conda install -y -c pytorch torchaudio

RUN python -m pip install --upgrade pip

#RUN pip install --no-cache-dir --upgrade torch
#RUN pip install --no-cache-dir --upgrade pandas awscli boto3 multi-model-server sagemaker-training sagemaker pytorch-igniter scipy torchvision matplotlib sagemaker-experiments torchaudio

RUN pip install --no-cache-dir --upgrade pandas awscli boto3 multi-model-server sagemaker-training sagemaker pytorch-igniter aws-sagemaker-remote scipy scikit-learn matplotlib sagemaker-experiments


#conda config --add channels soumith
# conda update pytorch torchvision
## conda install -y -c pytorch pytorch torchvision torchaudio cudatoolkit=10.2
# conda update -c pytorch pytorch torchvision torchaudio cudatoolkit=10.2

RUN python -c "import torch"
RUN python -c "import torchaudio"

# CMAKE
#RUN cd /home
#RUN curl -L https://github.com/Kitware/CMake/releases/download/v3.18.4/cmake-3.18.4.tar.gz | tar xz && cd cmake-3.18.4 && cmake . && make -j 4 && make install

# RUN apt update && apt install -qy build-essential autoconf libtool cmake ninja-build doxygen git python3-dev python3-pip zlib1g-dev libssl-dev libcurl4-openssl-dev

#RUN cd /home && git clone https://github.com/awslabs/ml-io.git
#RUN cd /home/ml-io && mkdir -p build/third-party && cd build/third-party && cmake ../../third-party && cmake --build . --target all
# build-tools/build-dependency third-party all 
#RUN cp /home/ml-io/third-party/lib/cmake/natsort/natsort-targets.cmake /home/ml-io/third-party/natsort
#RUN cd /home/ml-io && mkdir -p build/release && cd build/release && cmake -GNinja -DMLIO_INCLUDE_PYTHON_EXTENSION=on -DMLIO_BUILD_S3=on -DMLIO_INCLUDE_CONTRIB=on -DMLIO_INCLUDE_LIB=off -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_PREFIX_PATH="../third-party" ../..
#RUN cd /home/ml-io/build/release && cmake --build . && cmake --build . --target install 
#RUN cd /home/ml-io/build/release && cmake --build . --target mlio-py && cd /home/ml-io/src/mlio-py && python setup.py install

#python3-distutils  ?

#conda install -c conda-forge awscli
#RUN conda info --envs conda info -e
#RUN pip list
# wget https://github.com/Kitware/CMake/releases/download/v3.18.4/cmake-3.18.4.tar.gz
# curl https://github.com/Kitware/CMake/releases/download/v3.18.4/cmake-3.18.4.tar.gz | tar xz && cd cmake-3.18.4 && cmake . && make -j 4 && make install
# conda update -y conda
# conda update -y --all
# apt update && apt install -qy build-essential autoconf libtool cmake ninja-build doxygen git python3-dev python3-pip zlib1g-dev libssl-dev libcurl4-openssl-dev
#python3-distutils 
#build-tools/build-dependency build/third-party all
#$ mkdir build/release
#$ cd build/release
#$ cmake -GNinja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_PREFIX_PATH="$(pwd)/../third-party" ../..
#$ cmake --build .