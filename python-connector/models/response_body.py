"""Defines the ResponseBody model and related utilities for HTTP response handling.

This module provides:
- ResponseBody: a Pydantic model for HTTP responses;
- create_response: a helper function to create ResponseBody instances.
"""

import json
from typing import Any, ClassVar

from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import ModelReference as Reference
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field


class ResponseBody(BaseModel):  # noqa: D101
    status_code: int = Field(
        default=200,
        description="The HTTP status code of the response.",
        alias="StatusCode",
        example=200,
    )

    message: str = Field(
        default="Successfully",
        description="A message providing additional information about the response.",
        alias="Message",
        example="Successfully invoked `/set-config` with raw JSON in payload",
    )

    payload: Any = Field(
        default={},
        description="Json content of the response.",
        alias="Payload",
        example="",
    )

    value: str = Field(
        default="",
        description="The value returned by the operation, if applicable.",
        alias="Value",
        example="myResult",
    )

    class Config:  # noqa: D106
        arbitrary_types_allowed = True
        json_encoders: ClassVar = {
            Reference: lambda v: json.dumps(v, cls=AASToJsonEncoder),
            Submodel: lambda v: json.dumps(v, cls=AASToJsonEncoder)
        }


def create_response(status_code: int, message: str, payload: str = "{}", value: str = "") -> ResponseBody:
    """
    Create a ResponseBody instance with the given parameters.

    :param status_code: The HTTP status code of the response.
    :param message: A message providing additional information about the response.
    :param payload: Json content of the response.
    :param value: The value returned by the operation, if applicable.
    :return: An instance of ResponseBody.
    """
    body = ResponseBody()
    body.status_code = status_code
    body.message = message
    body.payload = payload
    body.value = value

    return body
