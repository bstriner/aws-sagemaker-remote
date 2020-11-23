# columbo-compute

FROM ubuntu:18.04
RUN apt-get update && \
  apt-get install -y libsvm3 sox python3-pip python3-dev ffmpeg wget curl git
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir --upgrade pandas awscli boto3 sagemaker scipy torch torchvision matplotlib mlflow

# LDC sph2pipe
RUN mkdir -p /home/sph2pipe \
	&& cd /home/sph2pipe \
	&& wget https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/ctools/sph2pipe_v2.5.tar.gz \
    && tar xzf sph2pipe_v2.5.tar.gz \
	&& cd sph2pipe_v2.5 \
	&& gcc -o sph2pipe *.c -lm \
	&& cp sph2pipe /bin

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python3", "--version"]
