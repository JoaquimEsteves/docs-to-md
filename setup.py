import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="docs2md",
    version="1.0.0",
    author="Joaquim Esteves",
    author_email="joaquimbve@hotmail.com",
    description="Automatically parse python docstrings and convert them to markdown!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoaquimEsteves/docs-to-md",
    packages=setuptools.find_packages(),
    license='GPLv3+',
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)