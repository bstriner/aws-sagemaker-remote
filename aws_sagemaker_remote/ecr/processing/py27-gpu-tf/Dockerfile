# columbo-compute

#FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04
#FROM ubuntu:18.04
FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

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
	libopenmpi-dev \
	python-dev \
	ffmpeg


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

#https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \

RUN curl -L -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh \
	&& chmod +x ~/miniconda.sh \
	&& ~/miniconda.sh -b -p /opt/conda \
	&& rm ~/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH

RUN conda init && conda init bash

RUN conda install -y -c anaconda -c dglteam -c mlio -c conda-forge   \
	python=2.7 \
	opencv \
	mkl \
	mkl-include 

	# numpy \
	# cython \
	# opencv \
	# scikit-learn \
	# pandas \
	# requests \
	# h5py \
	# pyopenssl \
	# dgl \ 
	# ipython \
	# dlib

RUN echo "conda activate" >> ~/.bashrc

#	opencv
#	mkl
	# \
	#mkl-include


#	tensorflow-gpu=1.4.1
#	numpy \
#	cython \
#	opencv \
#	scikit-learn \
#	pandas \
#	requests \
#	h5py \
#	pyopenssl \
#	dgl \ 
#	ipython \
#dlib
#	mkl \
# mkl-include \
#typing
#	pytorch torchvision 
#-c pytorch -c peterjc123
#torchaudio cudatoolkit=10.2
#\
#&& /opt/conda/bin/conda clean -ya \
#&& conda clean -ya

#RUN bash --login -c "python -c \"import torch\""
#RUN python -c "import torchaudio"
#RUN python -c "import torchvision"
#RUN python -c "import torchaudio"
#RUN python -c "import tensorflow"

# The following section uninstalls torch and torchvision before installing the
# custom versions from an S3 bucket. This will need to be removed in the future
#&& ln -s /opt/conda/bin/pip /usr/local/bin/pip3 \
RUN pip install --no-cache-dir --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN pip install --no-cache-dir -U \
	awscli \
	scipy \
	sagemaker \
	psutil \
	Pillow \
	matplotlib \
	boto3 \
	tensorflow-gpu==1.14.0 \
	pandas \
	numpy \
	dlib \
	scikit-image
#	fastai \
#	opencv-python
#	sagemaker-experiments \
#	smdebug \

#aws-sagemaker-remote \
#	pytorch-igniter \
#"sagemaker-pytorch-training<2" \
# && pip install --no-cache-dir -U https://pytorch-aws.s3-us-west-2.amazonaws.com/pytorch-1.5.0/py3/cpu/torch-1.5.0-cp36-cp36m-manylinux1_x86_64.whl \
# && pip uninstall -y torchvision \
# && pip install --no-deps --no-cache-dir -U \
#    https://torchvision-build.s3.amazonaws.com/1.5.0/cpu/torchvision-0.6.0-cp36-cp36m-linux_x86_64.whl

# LDC sph2pipe
# RUN mkdir -p /home/sph2pipe \
# 	&& cd /home/sph2pipe \
# 	&& wget https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/ctools/sph2pipe_v2.5.tar.gz \
# 	&& tar xzf sph2pipe_v2.5.tar.gz \
# 	&& cd sph2pipe_v2.5 \
# 	&& gcc -o sph2pipe *.c -lm \
# 	&& cp sph2pipe /bin


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
#RUN chmod +x /usr/local/bin/start_with_right_hostname.sh
#RUN curl -o /license.txt https://aws-dlc-licenses.s3.amazonaws.com/pytorch-1.5.0/license.txt
# Starts framework
#ENTRYPOINT ["bash", "-m", "start_with_right_hostname.sh"]

#RUN python -c "import torch"
#RUN python -c "import torchaudio"
#RUN python -c "import torchvision"
RUN python -c "import tensorflow"
#COPY start_container.sh /usr/local/bin/start_container.sh
#RUN chmod +x /usr/local/bin/start_container.sh
#RUN chmod +x /usr/local/bin/start_with_right_hostname.sh
#RUN curl -o /license.txt https://aws-dlc-licenses.s3.amazonaws.com/pytorch-1.5.0/license.txt
# Starts framework
#ENTRYPOINT ["bash","-m", "/usr/local/bin/start_container.sh"]
ENTRYPOINT ["/opt/conda/bin/conda","run"]
#ENTRYPOINT ["bash", "-m", "start_with_right_hostname.sh"]
#ENTRYPOINT ["/opt/conda/bin/conda","run","-n","pytorch"]
CMD ["/bin/bash"]
