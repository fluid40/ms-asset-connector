"""Defines the GetValuePayload model for handling AAS Reference deserialization."""

from typing import Any
from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import ModelReference as Reference
from pydantic import BaseModel, Field, PrivateAttr



class GetValuePayload(BaseModel):  # noqa: D101
    aid_ref_dict: dict = Field(..., alias="Reference")
    _aid_ref: Reference = PrivateAttr(default=None)

    def __init__(self, **data: Any):  # noqa: D107
        super().__init__(**data)
        self._aid_ref = AASFromJsonDecoder.object_hook(self.aid_ref_dict)
