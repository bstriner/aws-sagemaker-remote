from setuptools import find_packages, setup
import os
with open(os.path.abspath(os.path.join(__file__, '../README.rst')), encoding='utf-8') as f:
    long_description = f.read()
setup(name='aws-sagemaker-remote',
      version='0.0.7',
      author='Ben Striner',
      author_email="bstriner@gmail.com",
      url='https://github.com/bstriner/aws-sagemaker-remote',
      install_requires=[
          'sagemaker'
      ],
      description="Simplify running processing and training remotely on AWS SageMaker",
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type='text/x-rst')
