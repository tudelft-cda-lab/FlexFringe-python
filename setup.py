import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flexfringe-python",
    version="0.0.1",
    author="T. Catshoek",
    author_email="t.catshoek@tudelft.nl",
    description="Python wrapper for flexfringe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tudelft-cda-lab/FlexFringe-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'markdown',
        'graphviz',
        'pandas',
        'pillow'
    ],
)
