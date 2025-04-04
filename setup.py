# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open

# This call to setup() does all the work
setup(
    name="alphacast",
    version="0.1.8.5",
    description="Alphacast Python SDK",
    long_description="This Alphacast Python Library",
    long_description_content_type="text/markdown",
    url="https://alphacast-python-sdk.readthedocs.io/",
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
    packages=["alphacast"],
    include_package_data=True,
    install_requires=["requests", "pandas", "python-dotenv"]
)