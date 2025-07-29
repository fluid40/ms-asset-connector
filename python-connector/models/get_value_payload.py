"""Defines the GetValuePayload model for handling AAS Reference deserialization."""

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import ModelReference as Reference
from pydantic import BaseModel, Field, field_validator



class GetValuePayload(BaseModel):  # noqa: D101
    aid_ref: Reference = Field(..., alias="Reference")

    @field_validator("aid_ref", mode="before")
    def parse_aid_ref(cls, v):  # noqa: D102
        if isinstance(v, Reference):
            return v
        return AASFromJsonDecoder.object_hook(v)

    model_config = {"arbitrary_types_allowed": True}
