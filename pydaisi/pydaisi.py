import requests
import os
import uuid
import codecs
import dill
import json
import time
import logging

from dotenv import load_dotenv
from rich import pretty
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(markup=True)]
)

log = logging.getLogger(__name__)

pretty.install()
load_dotenv()

daisi_base_url = "https://app.daisi.io"
daisi_base_route = "/pebble-api/pebbles"
daisi_new_route = "/pebble-api/daisies"


def _load_dill_string(s):  # pragma: no cover
    return dill.loads(codecs.decode(s.encode(), "base64"))


def _get_dill_string(obj):  # pragma: no cover
    return codecs.encode(dill.dumps(obj, protocol=5), "base64").decode()


def _is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class DaisiExecution:
    def __init__(
        self, daisi, endpoint: str, arguments: dict
    ):
        self.id = None
        self.daisi = daisi
        self.endpoint = endpoint
        self.arguments = arguments
        self.status = "NOT_STARTED"
        self.result = None
        self.logs = []

        # Prepare the arguments
        parsed_args = self._pickle_hidden(self.arguments)
        parsed_args["_endpoint"] = self.endpoint

        self.parsed_args = parsed_args

    def _store_pickle(self, data):
        my_args = {"data": data}

        # Call the specified Daisi compute
        r = self.daisi.session.post(f"{self.daisi.base_url}/pickle", json=my_args)

        # Return the result
        return r.content.decode()

    def _pickle_hidden(self, args):
        final_args = {}
        for k, v in args.items():
            # First check if it's a DaisiExecution object
            if type(v) == DaisiExecution:
                # Grab the last result
                final_args[k] = v.result["outputs"][-1]["data"]
            elif not _is_jsonable(v):
                x = self._store_pickle(_get_dill_string(v))
                final_args[k] = "lookup:" + x
            else:
                final_args[k] = v

        return final_args

    def get_status(self):
        r = self.daisi.session.get(f"{self.daisi.base_url}/{self.daisi.id}/executions/{self.id}/status")

        self.status = r.json()

        return self.status

    def get_logs(self, limit=None):
        end_route = ""
        if limit:
            end_route = "?limit=" + str(limit)

        r = self.daisi.session.get(f"{self.daisi.base_url}/{self.daisi.id}/executions/{self.id}/logs" + end_route)

        res = r.json()
        if not limit:
            self.logs = r.json()

        return res

    def _unpickle_hidden(self, keep_pickle=False):
        final_output = []
        for result in self.result["outputs"]:
            if result["type"] in ["console-log", "data-grid"]:
                continue

            out = result["data"]
            if not keep_pickle and (type(out) == str and out.startswith("lookup:")):
                # Get the binary data
                l_split = out.split("lookup:")

                r = self.daisi.session.get(
                    f"{self.daisi.base_url}/pickle",
                    params={"lookup": l_split[1]}
                )

                out = _load_dill_string(r.content.decode())

                final_output.append(out)
            else:
                final_output.append(out)

        if len(final_output) == 1:
            final_output = final_output[0]

        return final_output

    def get_result(self, keep_pickle=False):
        if self.result:
            return self._unpickle_hidden()

        if self.status not in ["FINISHED", "FAILED"]:
            self.get_status()

        if self.status not in ["FINISHED", "FAILED"]:
            raise DaisiResponseNotReady(self.status)

        r = self.daisi.session.get(
            f"{self.daisi.base_url}/{self.daisi.id}/executions/{self.id}/results"
        )

        self.result = r.json()
        if "label" in self.result["outputs"][0] and self.result["outputs"][0]["label"] == "ERROR":
            self.status = "FAILED"

            error_id = self.result["outputs"][0]["data"]["id"]

            r = self.daisi.session.get(f"{self.daisi.base_url}/outputs/html/{error_id}")
            self.result = r.content.decode()

            return self.result

        return self._unpickle_hidden(keep_pickle=keep_pickle)


class Daisi:
    """
    A utility to assist in developing Daisis for the Daisi platform.

    A tool for creating, validating, publishing, and updating daisis.

    :param daisi_id: A daisi name or UUID
    :param base_url: The default URL to use for connecting to the daisi
    :param access_token: access token for authorizing to the platform
    """

    def __init__(
        self, daisi_id: str, *, base_url: str = daisi_base_url, access_token: str = ""
    ):
        """
        Daisi constructor method.

        :param daisi_id:  A Daisi name or UUID

        :raises ValueError: DaisiID Not Found (Non-200 response)
        """
        self.id = None
        self.name = None
        self.description = None
        self.endpoints = None
        self.base_url = base_url + daisi_base_route
        self.session = requests.Session()
        access_token = access_token or os.getenv("DAISI_ACCESS_TOKEN", "")
        self.new_url = base_url + daisi_new_route
        self.logger = logging.getLogger(__name__)

        if access_token:
            self.session.headers.update({"Authorization": f"token {access_token}"})

        # Check if it's a valid uuid:
        try:
            check_uuid = uuid.UUID(daisi_id) is not None
        except Exception as e:
            check_uuid = False

        if check_uuid:
            r = self.session.get(f"{self.base_url}/{daisi_id}")
            if r.ok:
                raise ValueError("The specified Daisi ID could not be found.")
            else:
                self.logger.info(f"Found existing Daisi: {r.json()['name']}")

                self.name = r.json()["name"]
                self.id = daisi_id
        else:
            self.logger.info(f"Calling {self.new_url}/search with query {daisi_id}")
            r = self.session.get(
                f"{self.new_url}/search",
                params={"term[]": [daisi_id], "pageSize": 1, "page": 1},
            )
            result = r.json()

            if result and result["success"] and result["data"]["data"]:
                self.name = daisi_id
                daisi_id = result["data"]["data"][0]["id"]
                self.logger.info(f"Found existing Daisi: {daisi_id}")
                self.id = daisi_id
            else:
                # TODO: Handle git repo connection here
                raise ValueError("That daisi could not be found.")

        # Call the specified Daisi endpoints
        r = self.session.get(f"{self.base_url}/{self.id}/endpoints")

        _endpoints = None
        if r.status_code == 200:
            _endpoints = r.json()

        self.endpoints = {x["name"]: x["schema"] for x in _endpoints}
        functionlist = list(self.endpoints.keys())
        for f in functionlist:
            self.__setattr__(
                f, (lambda f: (lambda s, *a, **kwa: s._run(f, *a, **kwa)).__get__(self))(f)
            )


    def _run(self, _func="compute", _defer_result=False, *args, **kwargs):
        param_names = [p["id"] for p in self.endpoints[_func]]
        kwargs.update(zip(param_names, args))

        # Grab a new DaisiExecution
        daisi_execution = DaisiExecution(
            daisi=self, endpoint=_func, arguments=kwargs
        )

        self.logger.info("[bold blue]=== BEGINNING DAISI EXECUTION WITH PARAMETERS ===[/bold blue]")
        self.logger.info(daisi_execution.parsed_args)
        self.logger.info("\n")

        r = self.session.post(
            f"{self.base_url}/{self.id}/executions", json=daisi_execution.parsed_args
        )

        result = None
        if r.status_code != 201:
            daisi_execution.status = "FAILED"
            self.logger.error("[bold red]=== DAISI EXECUTION FAILED ===[bold red]")

            return daisi_execution

        # Store the id
        daisi_execution.id = r.json()["id"]

        self.logger.info("[bold blue]=== DAISI EXECUTION STARTED: [/bold blue]" + daisi_execution.id + " [bold blue]===[/bold blue]")
        self.logger.info("\n")

        if _defer_result:
            self.logger.info("[bold orange]Execution is proceeding in the background:[/bold orange]")
            self.logger.info("get_status(): Fetch the status of the execution")
            self.logger.info("get_logs(): Fetch the logs of the execution")
            self.logger.info("get_result(): Fetch the result of the execution")

            return daisi_execution

        self.logger.info("[bold blue]=== DAISI EXECUTION LIVE LOGS ===[/bold blue]")
        while daisi_execution.status not in ["FINISHED", "FAILED"]:
            daisi_execution.get_status()

            log = daisi_execution.get_logs(limit=1)
            if log:
                self.logger.info("[yellow]" + log[0] + "[/yellow]")

            time.sleep(.25)

        self.logger.info("\n")
        self.logger.info("[bold green]=== DAISI EXECUTION FINISHED ===[/bold green]")
        self.logger.info("\n")

        self.logger.info("[bold blue]=== DAISI EXECUTION FINAL LOGS ===[/bold blue]")
        self.logger.info(daisi_execution.get_logs())

        self.logger.info("\n")
        self.logger.info("[bold blue]=== DAISI EXECUTION FINAL RESULTS ===[/bold blue]")
        self.logger.info(daisi_execution.get_result())

        return daisi_execution

    @staticmethod
    def get_daisies(base_url: str = daisi_base_url, access_token: str = ""):
        """
        Queries Daisi platform for a list of all current daisis.

        :return: List of daisis available on the Daisi platform.
        :rtype list
        """

        access_token = access_token or os.getenv("DAISI_ACCESS_TOKEN") or ""
        headers = {"Authorization": f"token {access_token}"} if access_token else None

        r = requests.get(
            f"{base_url}{daisi_new_route}", params={"pageSize": 10000, "page": 1}, headers=headers
        )
        result = r.json()

        return_list = []
        for daisi in result["data"]["data"]:
            return_list.append(
                {
                    "id": daisi["id"],
                    "name": daisi["name"],
                    "description": daisi["description"],
                }
            )

        final_return = sorted(return_list, key=lambda x: x["name"])

        return final_return


class DaisiResponseNotReady(Exception):
    def __init__(self, status):
        self.status = status
