import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="klprotools",
    version="0.0.1",
    author="Max Mäusezahl",
    author_email="maxmaeusezahl@googlemail.com",
    description="""A python package to interact with the 'KlimaLogg Pro' 
                   software""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmaeusezahl/klprotools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)