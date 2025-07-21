from typing import Any

# TODO: change these two imports if you're using Basyx
from aas_core3.types import Submodel
from aas_core3.types import Reference
import aas_core3.jsonization as aas_jsonization

from pydantic import BaseModel, Field, ConfigDict


class ResponseBody(BaseModel):

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

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            # TODO: replace with Basyx serialization logic if you wish
            Reference: lambda v: aas_jsonization.to_jsonable(v),
            Submodel: lambda v: aas_jsonization.to_jsonable(v)
        }


def create_response(status_code: int, message: str, payload=None, value: str = "") -> ResponseBody:
    """
    Create a ResponseBody instance with the given parameters.

    :param status_code: The HTTP status code of the response.
    :param message: A message providing additional information about the response.
    :param payload: Json content of the response.
    :param value: The value returned by the operation, if applicable.
    :return: An instance of ResponseBody.
    """
    if payload is None:
        payload = {}
    body = ResponseBody()
    body.status_code = status_code
    body.message = message
    body.payload = payload
    body.value = value

    return body
