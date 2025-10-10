"""FastAPI connector for handling `/set-config` and `/get-value` endpoints.

This module provides endpoints to set configuration and retrieve values using JSON payloads.
"""

import json
import threading
from typing import Dict, cast

import uvicorn
from basyx.aas.model import Submodel, SubmodelElementCollection
from fastapi import FastAPI

from python_connector.core.asset_connector import IAssetConnector
from python_connector.models.get_value_payload import GetValuePayload
from python_connector.models.response_body import ResponseBody, create_response
from python_connector.models.set_config_payload import SetConfigPayload
from python_connector.mqtt.mqtt_asset_connector import MqttAssetConnector
from python_connector.opc_ua.opcua_asset_connector import OpcuaAssetConnector
from python_connector.http_connector.http_asset_connector import HttpAssetConnector

app = FastAPI()


# Store AssetConnector instances mapped by (submodel id + interface idshort) in thread-safe way
connector_store: Dict[str, IAssetConnector] = {}
connector_store_lock = threading.Lock()


@app.get("/")
async def root():
    """Root endpoint that returns available endpoints."""
    return {"message": "Available endpoints are `/add-config` and `/get-value`"}


@app.post("/add-config")
async def add_or_update_config(payload: SetConfigPayload) -> ResponseBody:
    """Set configuration using a specific AID submodel."""
    aid_sm: Submodel = payload._aid_sm  # noqa: SLF001

    try:
        # iterate over all interface SMCs and create IAssetConnector for each of them
        for iface_smc in aid_sm.submodel_element:
            asset_connector: IAssetConnector = None
            if (
                iface_smc.supplemental_semantic_id[0].key[0].value
                == "http://www.w3.org/2011/mqtt"
            ):
                asset_connector = MqttAssetConnector(aid_sm.id, iface_smc)
            # TODO: confirm that is semanticId exists
            elif (
                iface_smc.supplemental_semantic_id[0].key[0].value
                == "http://www.w3.org/2011/opcua"
            ):
                asset_connector = OpcuaAssetConnector(aid_sm.id, iface_smc)
            elif (
                iface_smc.supplemental_semantic_id[0].key[0].value
                == "http://www.w3.org/2011/http"
            ):
                asset_connector = HttpAssetConnector(
                    aid_sm.id, cast(SubmodelElementCollection, iface_smc)
                )
            else:
                # TODO: check for other protocols
                pass

            connector_id = f"{aid_sm.id}-{iface_smc.id_short}"
            with connector_store_lock:
                connector_store[connector_id] = asset_connector

            await asset_connector.connect()

        return create_response(
            status_code=200,
            message="Successfully invoked `/set-config` with raw JSON in payload",
            payload=None,
            value=connector_id,
        )
    except Exception as e:
        return create_response(
            status_code=500,
            message=f"Error processing `/set-config`: {e!s}",
            payload=None,
        )


@app.post("/get-value")
async def get_value(payload: GetValuePayload) -> ResponseBody:
    """Get value from a specified protocol-specific endpoint in an AID submodel."""

    reference = payload._aid_ref
    aid_id = reference.key[0].value
    iface_smc = reference.key[1].value
    connector_id = f"{aid_id}-{iface_smc}"
    with connector_store_lock:
        asset_connector = connector_store.get(connector_id)
        if asset_connector is None:
            return create_response(
                status_code=404,
                message=f"No AssetConnector found for AID (decoded: {connector_id})",
                payload=None,
            )
        try:
            result = await asset_connector.get_value(payload._aid_ref)  # noqa: SLF001
            return create_response(
                status_code=200,
                message=f"Successfully invoked `/get-value` with raw JSON in payload",
                payload=json.loads(result) if result else None,
            )
        except Exception as e:
            return create_response(
                status_code=500,
                message=f"Error processing `/get-value`: {e!s}",
                payload=None,
            )


if __name__ == "__main__":
    """Run the FastAPI application."""
    uvicorn.run(app, host="0.0.0.0", port=8000)
