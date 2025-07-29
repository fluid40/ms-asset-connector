"""Defines the SetConfigPayload model for configuration payloads using Basyx and Pydantic."""

from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field, PrivateAttr, field_validator


class SetConfigPayload(BaseModel):  # noqa: D101
    aid_dict: dict = Field(..., alias="Aid")
    _aid_sm: Submodel = PrivateAttr(default=None)

    def __init__(self) -> None:
        #super().__init__()
        aid = self.aid_dict.get("Aid1", {})
        self._aid_sm = AASFromJsonDecoder.object_hook(aid)
