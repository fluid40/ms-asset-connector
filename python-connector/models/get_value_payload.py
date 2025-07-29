"""Defines the GetValuePayload model for handling AAS Reference deserialization."""

from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import ModelReference as Reference
from pydantic import BaseModel, Field, validator


class GetValuePayload(BaseModel):  # noqa: D101
    aid_ref: Reference = Field(..., alias="Reference")

    @validator("aid_ref", pre=True)
    def parse_aid_ref(cls, v: Any) -> Reference:  # noqa: D102
        if isinstance(v, Reference):
            return v
        return AASFromJsonDecoder.object_hook(v)

    class Config:  # noqa: D106
        arbitrary_types_allowed = True
