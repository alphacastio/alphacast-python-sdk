# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="alphacast-library",
    version="0.1.4",
    description="Alphacast Python library",
    long_description="This is the first version of Alphacast Python Library",
    long_description_content_type="text/markdown",
    url="https://alphacast-library.readthedocs.io/",
    author="Alphacast.io",
    author_email="hello@alphacast.io",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["alphacast_library"],
    include_package_data=True,
    install_requires=["requests", "pandas"]
)