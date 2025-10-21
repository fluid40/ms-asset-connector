"""Defines the SetValuePayload model for value payloads using Basyx and Pydantic."""

import json
from typing import Any

from basyx.aas.model import Key, KeyTypes, ModelReference
from pydantic import BaseModel, Field, PrivateAttr

KEY_TYPE_MAPPING: dict[str, str] = {
    "Submodel": "SUBMODEL",
    "SubmodelElementCollection": "SUBMODEL_ELEMENT_COLLECTION",
    "Property": "PROPERTY",
}


class SetValuePayload(BaseModel):  # noqa: D101
    aid_ref_dict: dict = Field(..., alias="Reference")
    value: Any = Field(..., alias="Value")
    _aid_ref: ModelReference = PrivateAttr(default=None)

    def __init__(self, **data: Any):  # noqa: D107
        super().__init__(**data)
        self._build_model_reference()

    def _build_model_reference(self) -> ModelReference:
        if self.aid_ref_dict is None:
            raise ValueError("AID Reference has not been initialized.")
        key_list = [Key(type_=self._get_key_type(key["type"]), value=key["value"]) for key in self.aid_ref_dict["keys"]]
        ref: ModelReference = ModelReference(key=tuple(key_list), type_=ModelReference)
        self._aid_ref = ref

    def _get_key_type(self, key_str: str) -> KeyTypes:
        key_type = KEY_TYPE_MAPPING.get(key_str)
        if key_type is None:
            raise ValueError(f"Unknown key type: {key_str}")
        return KeyTypes[key_type]
