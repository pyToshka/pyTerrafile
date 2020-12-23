# pyTerrafile

Simple script for management 3rd party external terraform modules.

Additionally, tfile supports modules from the Terraform Registry, as well as local modules and from git.
### Dependencies
Python version >=3.8
### Usage
Local

```shell script
usage: terrafile [-h] [-f [FILE]] [-p PATH] [-l LEVEL] [-F]

Terraform modules control

optional arguments:
  -h, --help            show this help message and exit
  -f [FILE], --file [FILE]
                        Tfile full path, if not present current directory
  -p PATH, --path PATH  Path for storing terraform modules, if not present current directory
  -l LEVEL, --level LEVEL
                        Terrafile level of logging
  -F, --force           Force re-download terraform modules from tfile
```
Via Docker

```shell script
docker run -it \
  --name pyterrafile --rm \
  -v "$(pwd)"/examples:/app kennyopennix/pyterrafile
```
### tfile structure
For Terraform Registry
```yaml
module-name:
  source: "source"
  version: "version"

```
`version` - git tag if not present by default `master`

For GIT
```yaml
module-name:
 source: git_url
 version: git_tag
 provider: provider_name
```
`version` - git tag if not present by default `master`
`provider` - could be aws,google,etc if not present by default `custom`

For local module
```yaml
terraform-k8s-vault-module:
  source: "module_path"
```

Example of tfile

```yaml
terraform-google-lb:
  source: "GoogleCloudPlatform/lb-http/google"
  version: "4.5.0"
terraform-aws-vpc:
 source: https://github.com/terraform-aws-modules/terraform-aws-vpc.git
 version: v2.64.0
 provider: aws
```

### Installation
From git

```shell script
python -m pip install git+https://github.com/pyToshka/pyTerrafile.git
```
Local installation
```shell script
git clone git@github.com:pyToshka/pyTerrafile.git
cd pyTerrafile
pip install .
```

Build docker image
```shell script
git clone git@github.com:pyToshka/pyTerrafile.git
cd pyTerrafile
docker build . -t  pyTerrafile
```
