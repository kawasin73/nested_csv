from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="nested_csv",
    version="0.1.0",
    author="Kawamura Shintaro",
    author_email="kawasin73@gmail.com",
    description="CSV generator for nested dict or list data structure such as"
    "JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kawasin73/nested_csv",
    packages=['nested_csv'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
