"""Defines the SetConfigPayload model for configuration payloads using Basyx and Pydantic."""

import json
from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field, PrivateAttr


class SetConfigPayload(BaseModel):  # noqa: D101
    aid_dict: dict = Field(..., alias="Aid", exclude=True)
    _aid_sm: Submodel = PrivateAttr(default=None)

    def __init__(self, **data: Any):  # noqa: D107
        super().__init__(**data)
        aid_string = json.dumps(self.aid_dict)
        self._aid_sm = json.loads(aid_string, cls=AASFromJsonDecoder)
        # self._aid_sm = AASFromJsonDecoder.object_hook(self.aid_dict) NOT WORKING FOR LOOPING ELEMENTS

