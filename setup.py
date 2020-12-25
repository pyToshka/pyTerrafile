from setuptools import setup

setup(
    name="terrafile",
    version="0.1.0",
    packages=("terrafile",),
    scripts=("bin/terrafile",),
    url="https://github.com/pyToshka/pyTerrafile",
    license="BSD",
    author="Yuriy Medvedev",
    author_email="medvedev.yp@gmail.com",
    description="Terraform file implementation for control modules",
    python_requires=">=3.8",
    long_description="""Simple script for management 3rd party external terraform modules.Additionally, tfile supports
    modules from the Terraform Registry, as well as local modules and from git.""",
    install_requires=(
        "PyYAML",
        "requests",
        "loguru",
        "GitPython",
        "python-hcl2",
        "nested-lookup",
    ),
)
