import json
import typing
from datetime import datetime, timedelta

from starlette.responses import Response


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


def int_to_datestr(value):
    s = str(value)
    fecnac = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
    return fecnac.strftime("%d/%m/%Y")
