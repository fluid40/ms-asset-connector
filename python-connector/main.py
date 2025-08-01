"""FastAPI connector for handling `/set-config` and `/get-value` endpoints.

This module provides endpoints to set configuration and retrieve values using JSON payloads.
"""

import json
from typing import TYPE_CHECKING

import uvicorn
from fastapi import FastAPI

from core import AIDParser, MQTTConnector
from models.get_value_payload import GetValuePayload
from models.response_body import ResponseBody, create_response
from models.set_config_payload import SetConfigPayload
from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import ReferenceElement, Submodel

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint that returns available endpoints.

    :return: A dictionary with a message listing available endpoints.
    """
    return {"message": "Available endpoints are `/set-config` and `/get-value`"}


@app.post("/set-config")
async def set_config(payload: SetConfigPayload) -> ResponseBody:
    """Set configuration endpoint.

    :param payload: The configuration payload to set.
    :return: A response indicating the result of the operation.
    """
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    try:
        # TODO: use AIDParser to process the AID Submodel
        aid_sm = payload._aid_sm
        aid_parser = AIDParser(aid_sm)
        topics_to_subscribe = aid_parser.get_mqtt_topics()
        mqtt_connector = MQTTConnector(aid_parser.base_url, topics_to_subscribe)
        mqtt_connector.start_async()

        # TODO: store the deserialized AID Submodel class, e.g., as global variable

        return create_response(
            status_code=200,
            message="Successfully invoked `/set-config` with raw JSON in payload",
            payload=aid_sm,
        )
    except Exception as e:
        return create_response(
            status_code=500,
            message=f"Error processing `/set-config`: {e!s}",
            payload=None,
        )


@app.post("/get-value")
async def get_value(payload: GetValuePayload) -> ResponseBody:
    """Get value endpoint.

    :param payload: The payload containing the reference to the value to retrieve.
    :return: A response containing the retrieved value.
    """
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    prop_ref: ReferenceElement = payload.aid_ref


    # TODO: use an AAS SDK to deserialize the content as Reference

    # TODO: find the SMC in the cached AID Submodel to which the reference points

    # TODO: read the details in the SMC and use it to establish a connection to the asset

    # TODO: return the value
    result = "myResult"

    return create_response(
        status_code=200,
        message="Successfully invoked `/get-value` with raw JSON in payload",
        payload=prop_ref,
        value=result,
    )


if __name__ == "__main__":
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=8090)
