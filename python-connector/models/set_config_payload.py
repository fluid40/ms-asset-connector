"""Defines the SetConfigPayload model for configuration payloads using Basyx and Pydantic."""

from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field, validator

BaseModel.arbitrary_types_allowed = True

class SetConfigPayload(BaseModel):  # noqa: D101
    aid_sm: Submodel = Field(..., alias="Aid", exclude=True)

    @validator("aid_sm", pre=True)
    def parse_aid_sm(cls, v: Any) -> Submodel:  # noqa: D102
        if isinstance(v, Submodel):
            return v
        return AASFromJsonDecoder.object_hook(v)

    class Config:  # noqa: D106
        arbitrary_types_allowed = True
