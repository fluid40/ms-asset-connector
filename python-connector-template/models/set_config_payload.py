from typing import Any

# TODO: change these two imports if you're using Basyx
from aas_core3.types import Submodel
import aas_core3.jsonization as aas_jsonization

from pydantic import BaseModel, Field, validator


BaseModel.arbitrary_types_allowed = True


class SetConfigPayload(BaseModel):
    """
    We introduce this class to wrap the configuration that is passed via the `set_config` POST method.
    For now, it only includes raw JSON content.

    The JSON content is exactly the AID submodel.
    We pass it raw to that you, the developer, can choose your favorite AAS SDK to deserialize it as Submodel class.
    """
    aid_sm: Submodel = Field(..., alias="Aid", exclude=True)

    @validator("aid_sm", pre=True)
    def parse_aid_sm(cls, v: Any) -> Submodel:
        if isinstance(v, Submodel):
            return v
        # TODO: replace with Basyx deserialization logic if you wish
        return aas_jsonization.submodel_from_jsonable(v)

    class Config:
        arbitrary_types_allowed = True
