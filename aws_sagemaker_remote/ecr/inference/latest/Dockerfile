FROM ubuntu:18.04

LABEL maintainer="Amazon AI"
LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true
LABEL com.amazonaws.sagemaker.capabilities.multi-models=true

ARG PYTHON_VERSION=3.8.6
#ARG PYTORCH_VERSION=1.5.0
#ARG TORCHVISION_VERSION=0.6.0
ARG MMS_VERSION=1.0.8

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8
ENV LD_LIBRARY_PATH /opt/conda/lib/:$LD_LIBRARY_PATH
ENV PATH /opt/conda/bin:$PATH
ENV SAGEMAKER_SERVING_MODULE sagemaker_pytorch_serving_container.serving:main
ENV TEMP=/home/model-server/tmp

SHELL ["/bin/bash", "--login", "-c"]
#--no-install-recommends
RUN apt-get update && apt-get install -y \
   build-essential \
   ca-certificates \
   cmake \
   curl \
   git \
   jq \
   libgl1-mesa-glx \
   libglib2.0-0 \
   libsm6 \
   libxext6 \
   libxrender-dev \
   openjdk-8-jdk-headless \
   vim \
   wget \
   zlib1g-dev \
   libsvm3 \
   sox \
   libsox-dev \
   apt-transport-https ca-certificates libcurl3-gnutls \
   openmpi-bin \
   libopenmpi-dev \
   libhogweed4 \
   ffmpeg

RUN curl -L -o ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
   && chmod +x ~/miniconda.sh \
   && ~/miniconda.sh -b -p /opt/conda \
   && rm ~/miniconda.sh \
   && /opt/conda/bin/conda update conda
RUN conda init && conda init bash
RUN echo "conda activate" >> ~/.bashrc
RUN /opt/conda/bin/conda install -y \
   -c anaconda \
   -c pytorch \
   -c conda-forge \
   python=$PYTHON_VERSION \
   cython \
   ipython \
   mkl-include \
   mkl \
   numpy \
   scipy \
   typing \
   pytorch torchvision torchaudio cpuonly \
   scikit-learn \
   pandas \
   h5py \
   requests \
   pyyaml 
#   && /opt/conda/bin/conda clean -ya
#RUN apt-get update
#opencv breaks apt
#RUN conda install -y -c anaconda -c conda-forge opencv 
#RUN apt-get update


RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN ln -s /opt/conda/bin/pip /usr/local/bin/pip3 
RUN pip install  --upgrade --no-cache-dir \
   "sagemaker-pytorch-inference<2" \
   opencv-python \
   mxnet-model-server \
   sagemaker-containers pillow awscli multi-model-server
#RUN pip install  --upgrade 

# Uninstall and re-install torch and torchvision from the PyTorch website
#RUN pip uninstall -y torch \
# && pip uninstall -y torchvision \
# && pip install torch==$PYTORCH_VERSION+cpu torchvision==$TORCHVISION_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN useradd -m model-server \
   && mkdir -p /home/model-server/tmp \
   && chown -R model-server /home/model-server

COPY mms-entrypoint.py /usr/local/bin/dockerd-entrypoint.py
COPY config.properties /home/model-server

RUN chmod +x /usr/local/bin/dockerd-entrypoint.py


#RUN curl https://aws-dlc-licenses.s3.amazonaws.com/pytorch-1.5.0/license.txt -o /license.txt

#RUN apt-get update

EXPOSE 8080 8081
ENTRYPOINT ["python", "/usr/local/bin/dockerd-entrypoint.py"]
CMD ["mxnet-model-server", "--start", "--mms-config", "/home/model-server/config.properties"]