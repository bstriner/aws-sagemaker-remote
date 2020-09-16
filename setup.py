from setuptools import find_packages, setup

setup(name='aws-sagemaker-remote',
      version='0.0.1',
      author='Ben Striner',
      url='https://github.com/bstriner/aws-sagemaker-remote',
      install_requires=[
          'sagemaker'
      ],
      packages=find_packages())

# python setup.py bdist_wheel sdist && twine upload dist\*
