from importlib.metadata import entry_points
from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='1.0.0',
    description='A framework for identifying and localizing leak events in a water distribution network.',
    author='Gabriel Marvin',
    author_email='gmarvin.work70@gmail.com'
    license='MIT',
    # entry_points={
    #     'console_scripts': [
    #         ''
    #     ],
    # }
)
