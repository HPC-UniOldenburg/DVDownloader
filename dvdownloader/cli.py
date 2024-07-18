import yaml
import typer
from typing_extensions import Annotated

from pydantic import BaseModel
from typing import List, Tuple
from dvdownloader.dvdownloader import DVDownloader 

class CliInput(BaseModel):
    api_token: str | None
    dataverse_url: str
    persistent_id: str

app = typer.Typer(add_completion=False)

@app.command()
def main(
    dataverse_url: Annotated[str, typer.Argument(
        help="The URL of the Dataverse repository.",
        show_default=False,
        )
    ],
    pid: str, # = typer.Option(
#        default=...,
#        help="The persistent identifier PID of the Dataverse dataset.",
#    ),
    api_token: str = typer.Option(
        default=None,
        help="The API_TOKEN for the Dataverse repository.",
    ),
):
    """
    Download files from a dataset with given DATAVERSE_URL and persistent identifier PID. Please
    provide an API_TOKEN if the dataset is not public.
    """

    cli_input = CliInput(
            api_token=api_token,
            dataverse_url=dataverse_url,
            persistent_id=pid,
            )

    downloader = DVDownloader(
        persistent_id=cli_input.persistent_id,
        dataverse_url=cli_input.dataverse_url,
        api_token=cli_input.api_token,
    )

    downloader.download()

if __name__ == "__main__":
    typer.run(main)
