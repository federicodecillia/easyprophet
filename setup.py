# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Setup functionality for the easyprophet package."""

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="easyprophet",  # directory name right below src/
    version="1.2.0",
    author="Federico De Cillia",
    description="Python package developed to simplify Prophet application to any data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/federicodecillia/easyprophet",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["easyprophet"],  # directory name right below src/
    install_requires=[
        "numpy",
        "pandas",
        "plotly",
        "scikit-learn",
        "scipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)
