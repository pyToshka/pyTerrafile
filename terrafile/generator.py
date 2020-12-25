import io
import json
import os
from glob import iglob
import logging

import hcl2
import yaml
from nested_lookup import nested_lookup


def tf_module_recursive(file_path):
    directory = file_path if file_path else os.getcwd()
    config_str = ""
    iterator = iglob(directory + "/*.tf")
    for fname in iterator:
        with open(fname, "r", encoding="utf-8") as f:
            config_str += f.read() + " "
    config_io = io.StringIO(config_str)
    config = hcl2.load(config_io)
    modules = {k: v for k, v in config.items() if k == "module"}
    return modules


def parse_tf(file_name):
    with open(file_name, "r") as file:
        modules_dict = hcl2.load(file)
        modules = {k: v for k, v in modules_dict.items() if k == "module"}

    return modules


def create_tfile(content, file_path):
    modules_dump = yaml.safe_load(json.dumps(content))
    module_name = []
    for key, value in modules_dump.items():
        for values in value:
            for module_names in values:
                module_name.append(module_names)
    modules_dict = []
    f = open(file_path, "w+")
    for names in module_name:
        source = nested_lookup(names, content, with_keys=True)
        data = json.loads(json.dumps(source))
        modules_dict.append(data)

    for modules in modules_dict:
        for modules_name in modules:
            for modules_data in modules[modules_name]:
                if modules_data["source"]:
                    source = " ".join([str(elem) for elem in modules_data["source"]])
                try:
                    if modules_data["version"]:
                        version = " ".join(
                            [str(elem) for elem in modules_data["version"]]
                        )
                except KeyError:
                    version = "master"
                ds = f"""
{modules_name}:
  source: {source}
  version: {version}
        """
        f.write(ds)
    f.close()


def generate(file_name, file_path, recursive=False):
    if recursive:
        create_tfile(tf_module_recursive(file_name), file_path)
    else:
        try:
            create_tfile(parse_tf(file_name), file_path)
        except IsADirectoryError:
            logging.error(
                "File not found. Please check terraform file for parsing or use recursive mode for modules "
                "folder"
            )
            exit(2)
