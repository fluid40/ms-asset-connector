"""FastAPI connector for handling `/set-config` and `/get-value` endpoints.

This module provides endpoints to set configuration and retrieve values using JSON payloads.
"""

import json

import uvicorn
from basyx.aas.adapter.json import AASFromJsonDecoder, AASToJsonEncoder
from basyx.aas.model import ModelReference, Submodel
from fastapi import FastAPI

from core import AIDParser, MQTTConnector, ReferenceResolver
from models.get_value_payload import GetValuePayload
from models.response_body import ResponseBody, create_response
from models.set_config_payload import SetConfigPayload

app = FastAPI()


topic_map: dict[str, str] = {}
mqtt_connector: MQTTConnector | None = None

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
        aid_sm: Submodel = payload._aid_sm  # noqa: SLF001
        aid_parser = AIDParser(aid_sm)
        mqtt_topics = aid_parser.get_mqtt_topics()
        connector = MQTTConnector(aid_parser.base_url, mqtt_topics)
        connector.start_async()

        global mqtt_connector
        mqtt_connector = connector

        # Assign the connector to the global variable
        # (do this outside the function, e.g., in a wrapper or after calling the endpoint)
        global topic_map
        topic_map = mqtt_topics

        return create_response(
            status_code=200,
            message="Successfully invoked `/set-config` with raw JSON in payload",
            payload=json.dumps(aid_sm, cls=AASToJsonEncoder),
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
    reference: ModelReference = payload.aid_ref_dict  # noqa: SLF001

    topic_name = ReferenceResolver.get_topic_by_reference(reference, topic_map)

    result = None
    if mqtt_connector is not None:
        result = json.loads(mqtt_connector.get_cached_value(topic_name))

    return create_response(
        status_code=200,
        message="Successfully invoked `/get-value` with raw JSON in payload",
        payload=payload,
        value=result,
    )


if __name__ == "__main__":
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=8090)
