"""FastAPI connector for handling `/set-config` and `/get-value` endpoints.

This module provides endpoints to set configuration and retrieve values using JSON payloads.
"""

import base64
import json
import threading

import uvicorn
from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import Submodel
from fastapi import FastAPI

from core.asset_connector import AssetConnector
from models.get_value_payload import GetValuePayload
from models.response_body import ResponseBody, create_response
from models.set_config_payload import SetConfigPayload

app = FastAPI()


# Store AssetConnector instances by submodel id (thread-safe)
connector_store: dict[str, AssetConnector] = {}
connector_store_lock = threading.Lock()


@app.get("/")
async def root():
    """Root endpoint that returns available endpoints."""
    return {"message": "Available endpoints are `/set-config` and `{{id}}/get-value`"}


# Set config for a specific AID submodel id
@app.post("/set-config")
async def add_or_update_config(payload: SetConfigPayload) -> ResponseBody:
    """Set configuration for a specific AID submodel id."""
    aid_sm: Submodel = payload._aid_sm  # noqa: SLF001
    try:
        connector_id: str = base64.urlsafe_b64encode(str(aid_sm.id).encode()).decode()

        asset_connector = AssetConnector(connector_id)
        asset_connector.set_config(aid_sm)
        with connector_store_lock:
            connector_store[connector_id] = asset_connector
        return create_response(
            status_code=200,
            message="Successfully invoked `/set-config` with raw JSON in payload",
            payload=None,
            value=connector_id
        )
    except (ValueError, RuntimeError, ConnectionError) as e:
        return create_response(
            status_code=500,
            message=f"Error processing `/set-config`: {e!s}",
            payload=None,
        )


# Get value for a specific AID submodel id
@app.post("/{id}/get-value")
async def get_value(id: str, payload: GetValuePayload) -> ResponseBody:
    """Get value for a specific AID submodel id."""
    with connector_store_lock:
        asset_connector = connector_store.get(id)
    decoded_id: str = base64.urlsafe_b64decode(id.encode()).decode()
    if asset_connector is None:
        return create_response(
            status_code=404,
            message=f"No AssetConnector found for id {decoded_id}",
            payload=None,
        )
    try:
        result = asset_connector.get_value(payload._aid_ref)  # noqa: SLF001
        return create_response(
            status_code=200,
            message=f"Successfully invoked `/get-value/{id}` with raw JSON in payload",
            payload=payload,
            value=json.loads(result, cls=AASToJsonEncoder) if result else None,
        )
    except (ValueError, RuntimeError, ConnectionError) as e:
        return create_response(
            status_code=500,
            message=f"Error processing `/get-value/{id}`: {e!s}",
            payload=None,
        )


if __name__ == "__main__":
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=8090)
