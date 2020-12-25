import argparse
import logging
import os

from terrafile import install
from terrafile.generator import generate

loglevel = "ERROR"
current_path = os.path.abspath(os.getcwd())
parser = argparse.ArgumentParser(
    prog="terrafile", description="Terraform modules control"
)
parser.add_argument(
    "-a",
    "--action",
    choices=["sync", "generate"],
    nargs="?",
    default="sync",
    const="sync",
    help="Start/Stop or Restart list of services or service",
)
parser.add_argument(
    "-f", "--file", nargs="?", help="Tfile full path, if not present current directory"
)
parser.add_argument(
    "-p",
    "--path",
    help="Path for storing terraform modules, if not present current directory",
)
parser.add_argument("-l", "--level", help="Terrafile level of logging")
parser.add_argument(
    "-F",
    "--force",
    action="store_true",
    help="Force re-download terraform modules from tfile",
)
parser.add_argument(
    "-m",
    "--module_path",
    help="Terraform module file, if you want to parse tf files in recursive "
    "mode please add -r flag",
)
parser.add_argument(
    "-r",
    "--recursive",
    help="Recursive mode for parsing directory with terraform modules",
    action="store_true",
)
args = parser.parse_args()
if args.file:
    tfile = args.file
else:
    tfile = f"{current_path}/tfile"
if args.path:
    module_path = args.path
else:
    module_path = current_path
if args.level:
    loglevel = args.level.upper()
if "PYTERRAFILE_LOGLEVEL" in os.environ:
    loglevel = os.environ["PYTERRAFILE_LOGLEVEL"]
if args.force:
    download_force = True
else:
    download_force = False
try:
    import http.client as http_client
except ImportError as error:
    raise error
if loglevel == "DEBUG":
    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel("DEBUG")
    requests_log.propagate = True
else:
    http_client.HTTPConnection.debuglevel = 0
if "sync" in args.action:
    install(tfile, module_path, loglevel, download_force)
elif "generate" in args.action:
    if not args.module_path:
        logging.error("key -m is mandatory for generating tfile from terraform files")
        exit(2)
    if args.recursive:
        generate(args.module_path, tfile, recursive=True)
    else:
        generate(args.module_path, tfile)
