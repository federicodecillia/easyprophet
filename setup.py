# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Setup functionality for the prophet_pack package."""

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="prophet_pack",  # directory name right below src/
    version="2021.1",
    author="Federico De Cillia",
    description="Python package developed to simplify Prophet application to any data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/federicodecillia/prophet_pack",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["prophet_pack"], # directory name right below src/
    install_requires=[
        "numpy",
        "pandas",
        ],
    classifiers=[],
    python_requires=">=3.7"
)
