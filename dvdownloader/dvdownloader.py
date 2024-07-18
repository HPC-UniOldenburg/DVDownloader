import os
from pydantic import BaseModel, validator
import requests
from urllib.parse import urljoin
import json
from dotted_dict import DottedDict
import typer

class DVDownloader(BaseModel):
    """
    A class for downloading files from a dataset in a Dataverse repository.

    Methods:
        download(persistent_id: str, dataverse_url: str, api_token: str) -> None:
            Downloads the files from the specified Dataverse repository.

    """
    api_token: str | None
    dataverse_url: str
    persistent_id: str


    def _parse_raw_list(self, raw_list):
        """
        Reduce the raw_list returned by Dataverse API to the needed values only.

        Returns: 
            list: a list of DottedDict() items each holding information about
                  a file in the dataset
        """
        list = []
        for entry in raw_list:
            parsed_entry            = DottedDict()
            parsed_entry.filename   = entry.dataFile.filename
            parsed_entry.file_id    = entry.dataFile.id
            parsed_entry.filesize   = entry.dataFile.filesize
            parsed_entry.checksum   = entry.dataFile.checksum
            parsed_entry.directory  = ""
            if 'directoryLabel' in entry:
                parsed_entry.directory  = entry.directoryLabel
            parsed_entry.dataset_id = entry.datasetVersionId
            list.append(parsed_entry)

        return list

    def _retrieve_dataset_files(self):
        """
        Retrieve the files of a specific dataset from a Dataverse repository.

        Returns:
            list: A list of files in the dataset.

        Raises:
            HTTPError: If the request to the Dataverse repository fails.
        """

        DATASET_ENDPOINT = "/api/datasets/:persistentId/?persistentId={0}"

        if self.api_token:
            response = requests.get(
                           urljoin(self.dataverse_url, DATASET_ENDPOINT.format(self.persistent_id)),
                           headers={"X-Dataverse-key": self.api_token},
                           )
        else:
            response = requests.get(
                           urljoin(self.dataverse_url, DATASET_ENDPOINT.format(self.persistent_id)))
      
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Could not download dataset '{self.persistent_id}' at '{self.dataverse_url}' \
                    \n\n{json.dumps(response.json(), indent=2)}"
            )

        raw_list = DottedDict(response.json()).data.latestVersion.files
        list     = self._parse_raw_list(raw_list)

        return list

    def download(self):
        """
        Downloads the files from a dataset in a Dataverse repository
        """
        root_dir = self.persistent_id.split("/")[-1]
        DATAFILE_ENDPOINT = "/api/access/datafile/{0}"
        try:
            files_in_dataset = self._retrieve_dataset_files()
        except requests.exceptions.RequestException as e:
            print(f'Unable to retrieve dataset file list from {self.dataverse_url}. See error message:')
            print(e)
            raise typer.Exit(code=1)
        
        for file_dd in files_in_dataset:
            file_name = file_dd.filename
            file_path = os.path.join(root_dir, file_dd.directory)
            file_id   = file_dd.file_id
            print("Downloading %s/%s ..." % (file_path, file_name))
            if self.api_token:
                response = requests.get(
                                        urljoin(self.dataverse_url, 
                                        DATAFILE_ENDPOINT.format(file_id)),
                                        headers={"X-Dataverse-key": self.api_token},
                                       )
            else:
                response = requests.get(
                                        urljoin(self.dataverse_url, 
                                        DATAFILE_ENDPOINT.format(file_id)),
                                       )

            if response.status_code != 200:
                raise requests.HTTPError(f"Could not download datafile '{file_name}' at '{self.dataverse_url}' \
                                           \n\n{json.dumps(response.json(), indent=2)}")
                raise typer.Exit()

            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except:
                    print(f'Could not create directory {file_path}')
                    raise typer.Exit()

            try:
                open(os.path.join(file_path, file_name), 'wb').write(response.content)
            except: 
                print(f'Could not save file {file_name}')
                raise typer.Exit()

