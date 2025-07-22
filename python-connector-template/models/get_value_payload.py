from typing import Any

# TODO: change these two imports if you're using Basyx
from aas_core3.types import Reference
import aas_core3.jsonization as aas_jsonization

from pydantic import BaseModel, Field, validator


class GetValuePayload(BaseModel):
    """
    We introduce this class to wrap the parameters that are passed via the `get_value` GET method.
    For now, it only includes raw JSON content.

    The JSON content is a Reference (AAS type) to a property in the AID submodel.
    We pass it raw to that you, the developer, can choose your favorite AAS SDK to deserialize it as Reference class.
    """
    aid_ref: Reference = Field(..., alias="Reference")

    @validator("aid_ref", pre=True)
    def parse_aid_ref(cls, v: Any) -> Reference:
        if isinstance(v, Reference):
            return v
        # TODO: replace with Basyx deserialization logic if you wish
        return aas_jsonization.reference_from_jsonable(v)

    class Config:
        arbitrary_types_allowed = True
