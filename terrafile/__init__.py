import os
import shutil
import sys
from os import path

import git
import requests
import yaml
from git import Repo, Git, GitCommandError
from loguru import logger

TF_REGISTRY_BASE_URL = "https://registry.terraform.io/v1/modules"


class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(f"Downloading: ({op_code}, {cur_count}, {max_count}, {message})")


class Formatter:
    def __init__(self):
        self.padding = 0
        self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"

    def format(self, record):
        length = len("{name}:{function}:{line}".format(**record))
        self.padding = max(self.padding, length)
        record["extra"]["padding"] = " " * (self.padding - length)
        return self.fmt


formatter = Formatter()


def check_source(source):
    if source.startswith("https://") or "@" in source:
        logger.debug(f"Detected GIT based module for source {source}")
        return "git"
    if source.startswith("../") or source.startswith("./") or source.startswith("/"):
        logger.debug(f"Detected local based module for source {source}")
        return "local"
    if source.startswith(""):
        logger.debug(f"Detected local based module for source {source}")
        return "registry"


def check_directory(name):
    logger.info(f"Checking directory {name}")
    directory = str(path.exists(f"{name}"))
    if directory:
        logger.debug(f"Directory {name} exist")
        return os.path.abspath(f"{name}")
    else:
        logger.debug(f"Directory {name} doesn't exist, creating directory")
        os.mkdir(directory)
        logger.debug(f"Directory {name} has been created")
        return os.path.abspath(f"{name}")


def git_module(source, module_path, name, tag=None):
    check_path = check_directory(module_path)
    logger.info(f"Checkout new module {name}")
    try:
        Repo.clone_from(source, f"{check_path}/{name}", progress=Progress())
    except GitCommandError as error:
        logger.debug(f"During checkout error {error} has been detected")
        pass
    git_version = Git(f"{check_path}/{name}")
    if tag is not None:
        logger.info(f"Getting {tag} for module {name}")
        git_version.checkout(tag)

    else:
        logger.info(f"{tag} hasn't present for module {name}, checkout master branch")
        git_version.checkout("master")


def registry_module(source, version):
    name, namespace, provider = source.split("/")
    module_url = f"{TF_REGISTRY_BASE_URL}/{name}/{namespace}/{provider}/{version}"
    response = requests.get(module_url)
    logger.info(
        f"Got information for {response.json()['name']}, "
        f"Module url is {response.json()['source']},"
        f"provider is {response.json()['provider']}"
    )
    return (
        response.json()["source"],
        response.json()["tag"],
        response.json()["name"],
        response.json()["provider"],
    )


def local_module(source, destination):
    try:
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(
            source, destination, dirs_exist_ok=True, copy_function=shutil.copy
        )
    except shutil.Error as exc:
        errors = exc.args[0]
        for error in errors:
            source, destination, msg = error
            shutil.copy2(source, destination)


def read_tf_file(tfile=None):
    with open(tfile) as terrafile:
        tf_file = yaml.safe_load(terrafile)
    return tf_file


def install(terrafile, module_path=None, log_level=None, download_force=False):
    level = log_level.upper()
    logger.remove()
    logger.add(sys.stderr, format=formatter.format, level=level)
    if download_force:
        shutil.rmtree(f"{module_path}/vendors")
    if os.path.isfile(terrafile) and os.path.getsize(terrafile) == 0:
        logger.error("tfile is empty, please check tfile")
        sys.exit(2)
    try:
        terrafile = read_tf_file(terrafile)
    except FileNotFoundError:
        logger.error(
            "tfile does not exist or is not correct, please create file in current directory or provide "
            "existing file"
        )
        sys.exit(2)
    try:
        for name, details in sorted(terrafile.items()):
            if "provider" in details:
                provider = details["provider"]
            else:
                provider = "custom"
            module_type = check_source(details["source"])
            if module_type == "registry":
                url, version, name, provider = registry_module(
                    details["source"], details["version"]
                )
                git_module(url, f"{module_path}/vendors/{provider}", name, version)
            elif module_type == "local":
                local_module(
                    details["source"], f"{module_path}/vendors/{provider}/{name}"
                )
            elif module_type == "git":
                git_module(
                    details["source"],
                    f"{module_path}/vendors/{provider}",
                    name,
                    details["version"],
                )
    except AttributeError as error:
        logger.error(f"tfile is not correct, please check tfile format {error}")
