# see https://github.com/aws/sagemaker-pytorch-training-toolkit/
# https://aws-dlc-licenses.s3.amazonaws.com/pytorch-1.5.0/license.txt

FROM ubuntu:18.04

ARG PYTHON_VERSION=3.8
#ARG OPEN_MPI_VERSION=4.0.1

#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/conda/lib"
ENV PATH=/opt/conda/bin:$PATH
ENV SAGEMAKER_TRAINING_MODULE=sagemaker_pytorch_container.training:main
ENV DGLBACKEND=pytorch

SHELL ["/bin/bash", "--login", "-c"]

WORKDIR /

#--no-install-recommends 
RUN apt-get update \
  && apt-get install -y \
  ca-certificates \
  cmake \
  curl \
  git \
  wget \
  vim \
  build-essential \
  jq \
  libglib2.0-0 \
  libgl1-mesa-glx \
  libsm6 \
  libxext6 \
  libxrender-dev \
  zlib1g-dev \
  software-properties-common \
  libsvm3 \
  sox \
  libsox-dev \
  openmpi-bin \
  libopenmpi-dev

# sudo apt-get install --reinstall openmpi-bin libopenmpi-dev


#RUN wget https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-$OPEN_MPI_VERSION.tar.gz \
#  && gunzip -c openmpi-$OPEN_MPI_VERSION.tar.gz | tar xf - \
#  && cd openmpi-$OPEN_MPI_VERSION \
#  && ./configure --prefix=/home/.openmpi \
#  && make all install \
#  && cd .. \
#  && rm openmpi-$OPEN_MPI_VERSION.tar.gz \
#  && rm -rf openmpi-$OPEN_MPI_VERSION

# The ENV variables declared below are changed in the previous section
# Grouping these ENV variables in the first section causes
# ompi_info to fail. This is only observed in CPU containers
#ENV PATH="$PATH:/home/.openmpi/bin"
#ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/.openmpi/lib/"
#RUN ompi_info --parsable --all | grep mpi_built_with_cuda_support:value
#https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN curl -L -o ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  && chmod +x ~/miniconda.sh \
  && ~/miniconda.sh -b -p /opt/conda \
  && rm ~/miniconda.sh

RUN conda update conda
RUN conda init bash
#RUN conda create --name pytorch -y python=$PYTHON_VERSION
#ENV PATH=/opt/conda/envs/pytorch/bin:$PATH
#RUN bash -c "conda init bash"
#RUN conda init bash
RUN echo "conda activate" >> ~/.bashrc
#RUN conda run -n pytorch conda install -y \
#RUN bash --login -c "conda init bash"
RUN conda install -y \
  -c mlio \
  -c pytorch \
  -c conda-forge \
  -c dglteam \
  python=$PYTHON_VERSION \
  numpy \
  ipython \
  mkl \
  mkl-include \
  cython \
  typing \
  pyopenssl \
  opencv \
  scikit-learn \
  pandas \
  h5py \
  requests \
  dgl \
  pytorch \
  torchvision \
  torchaudio \
  cpuonly \
  mlio-py \
  mlio-py libmlio
# \
#&& conda run -n pytorch clean -ya \
#&& conda clean -ya

#RUN conda init bash

# Activate the environment, and make sure it's activated:
#RUN echo "conda activate pytorch" >> ~/.bashrc

#&& /opt/conda/bin/conda install -y \-c anaconda \
#python=$PYTHON_VERSION \
#numpy==1.16.4 \
#ipython==7.10.1 \
#mkl==2019.4 \
#mkl-include==2019.4 \
#cython==0.29.12 \
#typing==3.6.4 \
#"pyopenssl>=17.5.0" \
#&& conda install -c conda-forge \
#opencv==4.0.1 \
#&& conda install -y \
#scikit-learn==0.21.2 \
#pandas==0.25.0 \
#h5py==2.9.0 \
#requests==2.22.0 \
#&& conda install -c dglteam -y dgl==0.4.3 \
#&& conda install -y pytorch torchvision torchaudio cpuonly -c pytorch \
#&& conda install -y -c mlio -c conda-forge mlio-py libmlio \
#&& /opt/conda/bin/conda clean -ya \
#&& conda clean -ya

#RUN conda install -y -c mlio -c conda-forge mlio-py libmlio libmlio-dbg libmlio-devel


#ENV PATH=/opt/conda/envs/pytorch/bin:$PATH
#RUN conda init bash
#RUN conda update conda

#RUN rm /usr/local/bin/pip && ln -s /opt/conda/envs/pytorch/bin/pip /usr/local/bin/pip
#RUN rm /usr/local/bin/pip3 && ln -s /opt/conda/envs/pytorch/bin/pip /usr/local/bin/pip3
#RUN rm /usr/local/bin/python && ln -s /opt/conda/envs/pytorch/bin/python /usr/local/bin/python
#RUN rm /usr/local/bin/python3 && ln -s /opt/conda/envs/pytorch/bin/python /usr/local/bin/python3

#RUN conda run -n pytorch python -c "import torch"
#RUN conda run -n pytorch python -c "import torchaudio"
#RUN conda run -n pytorch python -c "import torchvision"
#RUN conda run -n pytorch python -c "import mlio"

RUN python -c "import torch"
RUN python -c "import torchaudio"
RUN python -c "import torchvision"
RUN python -c "import mlio"


RUN python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org \
  #   && ln -s /opt/conda/bin/pip /usr/local/bin/pip3 \
  && python -m pip install --no-cache-dir -U \
  awscli \
  fastai \
  scipy \
  smdebug \
  sagemaker \
  psutil \
  Pillow \
  sagemaker-experiments \
  sagemaker-pytorch-training \
  matplotlib \
  aws-sagemaker-remote \
  pytorch-igniter


RUN python -c "import torch"
RUN python -c "import torchaudio"
RUN python -c "import torchvision"
RUN python -c "import mlio"

#"sagemaker-pytorch-training<2" \
# && pip install --no-cache-dir -U https://pytorch-aws.s3-us-west-2.amazonaws.com/pytorch-1.5.0/py3/cpu/torch-1.5.0-cp36-cp36m-manylinux1_x86_64.whl \
# && pip uninstall -y torchvision \
# && pip install --no-deps --no-cache-dir -U \
#    https://torchvision-build.s3.amazonaws.com/1.5.0/cpu/torchvision-0.6.0-cp36-cp36m-linux_x86_64.whl

#RUN conda install -y pytorch torchvision torchaudio cudatoolkit=11.0 -c pytorch \
#RUN conda install -y pytorch torchvision torchaudio cpuonly -c pytorch \
# && /opt/conda/bin/conda clean -ya \
# && conda clean -ya

#RUN conda install -y -c mlio -c conda-forge mlio-py libmlio \
# && /opt/conda/bin/conda clean -ya \
# && conda clean -ya

# Copy workaround script for incorrect hostname
# COPY changehostname.c /
# COPY start_with_right_hostname.sh /usr/local/bin/start_with_right_hostname.sh
#COPY start_container.sh /usr/local/bin/start_container
#RUN chmod +x /usr/local/bin/start_with_right_hostname.sh
#RUN curl -o /license.txt https://aws-dlc-licenses.s3.amazonaws.com/pytorch-1.5.0/license.txt
# Starts framework
#ENTRYPOINT ["bash", "-m", "start_with_right_hostname.sh"]
ENTRYPOINT ["/opt/conda/bin/conda","run"]
CMD ["/bin/bash"]
#"conda", "run", "-n", "myenv", "/bin/bash", "-c"