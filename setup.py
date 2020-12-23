from setuptools import setup

setup(
    name="terrafile",
    version="0.1.0",
    packages=("terrafile",),
    scripts=("bin/terrafile",),
    url="",
    license="BSD",
    author="Yuriy Medvedev",
    author_email="medvedev.yp@gmail.com",
    description="Terraform file implementation for control modules",
    python_requires=">=3.8",
    install_requires=("PyYAML", "requests", "loguru", "GitPython"),
)
