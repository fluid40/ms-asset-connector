"""Defines the SetConfigPayload model for configuration payloads using Basyx and Pydantic."""

from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field, PrivateAttr, field_validator


class SetConfigPayload(BaseModel):  # noqa: D101
    aid_dict: dict = Field(..., alias="Aid", exclude=True)
    _aid_sm: Submodel = PrivateAttr(default=None)

    def __init__(self, **data: Any):  # noqa: D107
        super().__init__(**data)

        self._aid_sm = AASFromJsonDecoder.object_hook(self.aid_dict)

