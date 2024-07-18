== Overview
DVDownloader is a simple Python code to download files from a dataset in a Dataverse repository (https://dataverse.org/). It use HTTP-requests to access the native API of Dataverse. A similar tool is the python-dvuploader (https://github.com/gdcc/python-dvuploader) from which the idea for this project was sparked and some of the code was borrowed.

== Usage
To install download the latest release as tarball and run
```
pip install dvdownloader-0.1.0.tar.gz
```
Download a dataset with
```
dvdownloader https://your.dataverse.repo.org/ doi:10.00000/ABCD3F
```
You can add an optional API token with `--api-token` to download private datasets. 

