import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname("__file__"))

version = {}
with open(os.path.join(here, "ddm", "__version__.py")) as f:
    exec(f.read(), version)


with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="ddm",
    version=version["__version__"],
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/koenderinklab/ddmPilotCode",
    author="Iain Muntz, James Conboy, Irene Isturiz",
    author_email="i.a.a.muntz@tudelft.nl",
    license="Apache Software License 2.0",
    packages=find_packages(exclude=["*tests*"]),
    key_words=["differential dynamic micorscopy", "biological soft matter"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
    install_requires=[
        "numpy",
        "jpype1>0.6",
        "numba",
        "nd2",
        "nd2reader",
        "pims",
        "pyfftw",
        "scipy",
        "readlif",
    ],
    extras_require={
        "dev": ["black", "bump2version", "pytest==4.6.2", "pytest-cov", "sphinx"]
    },
)
