"""FastAPI connector for handling `/set-config` and `/get-value` endpoints.

This module provides endpoints to set configuration and retrieve values using JSON payloads.
"""

import json
import logging
import os
import threading
from typing import cast

import uvicorn
from aas_standard_parser import collection_helpers
from basyx.aas.model import Submodel, SubmodelElementCollection
from fastapi import FastAPI, HTTPException

from .core.asset_connector import IAssetConnector
from .http_connector.http_asset_connector import HttpAssetConnector
from .models.get_value_payload import GetValuePayload
from .models.response_body import ResponseBody, create_response
from .models.set_config_payload import SetConfigPayload
from .models.set_value_payload import SetValuePayload
from .mqtt.mqtt_asset_connector import MqttAssetConnector
from .opc_ua.opcua_asset_connector import OpcuaAssetConnector

app = FastAPI()

logger = logging.getLogger(__name__)

# Store AssetConnector instances mapped by (submodel id + interface idshort) in thread-safe way
connector_store: dict[str, IAssetConnector] = {}
connector_store_lock = threading.Lock()


@app.get("/")
async def root() -> ResponseBody:
    """Root endpoint that returns available endpoints."""
    return create_response(status_code=200, message="Available endpoints are `/add-config` and `/get-value`", payload=None)


@app.post("/add-config")
async def add_or_update_config(payload: SetConfigPayload) -> ResponseBody:
    """Set configuration using a specific AID submodel."""
    aid_sm: Submodel = payload._aid_sm  # noqa: SLF001

    logger.info(f"Received `/set-config` request with AID submodel ID: {aid_sm.id}")

    error_messages = []

    try:
        # iterate over all interface SMCs and create IAssetConnector for each of them
        for iface_smc in aid_sm.submodel_element:
            asset_connector: IAssetConnector = None

            if iface_smc.supplemental_semantic_id is None or len(iface_smc.supplemental_semantic_id) == 0:
                logger.warning(f"Skipping interface submodel '{iface_smc.id_short}' as it has no supplemental semantic ID")
                continue

            if collection_helpers.contains_supplemental_semantic_id(iface_smc, "http://www.w3.org/2011/mqtt"):
                logger.info("Creating MQTT AssetConnector")
                asset_connector = MqttAssetConnector(aid_sm.id, iface_smc)

            elif collection_helpers.contains_supplemental_semantic_id(iface_smc, "http://www.w3.org/2011/opcua"):
                logger.info("Creating OPC UA AssetConnector")
                asset_connector = OpcuaAssetConnector(aid_sm.id, iface_smc)

            elif collection_helpers.contains_supplemental_semantic_id(iface_smc, "http://www.w3.org/2011/http"):
                logger.info("Creating HTTP AssetConnector")
                asset_connector = HttpAssetConnector(aid_sm.id, cast(SubmodelElementCollection, iface_smc))
                # TODO: check for other protocols

            else:
                logger.warning(
                    f"Unsupported protocol '{iface_smc.supplemental_semantic_id[0].key[0].value}' in interface submodel '{iface_smc.id_short}'."
                )
                continue

            connector_id = f"{aid_sm.id}-{iface_smc.id_short}"
            logger.debug(f"Storing AssetConnector with ID '{connector_id}'")
            with connector_store_lock:
                connector_store[connector_id] = asset_connector

            try:
                await asset_connector.connect()
            except Exception as e:
                logger.error(f"Failed to connect AssetConnector to '{asset_connector.base}': {e}")
                error_messages.append(f"Failed to connect AssetConnector to '{asset_connector.base}': {e}")

            if asset_connector.is_connected:
                logger.debug(f"Successfully connected AssetConnector to '{asset_connector.base}'")
            else:
                logger.error(f"AssetConnector to '{asset_connector.base}' is not connected after connect attempt")
                error_messages.append(f"AssetConnector to '{asset_connector.base}' is not connected after connect attempt")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}") from e

    # search not connected connectors
    with connector_store_lock:
        connected = [connector_id for connector_id, asset_connector in connector_store.items() if asset_connector.is_connected]

    if len(connected) == 0:
        errors: str = "; ".join(error_messages)
        raise HTTPException(status_code=500, detail=errors)

    logger.debug(f"Connected AssetConnectors after `/set-config`: {len(connected)}")

    return create_response(
        status_code=200,
        message="Successfully invoked `/set-config` with raw JSON in payload",
        payload=None,
        value=connector_id,
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
                status_code=200, message="Successfully invoked `/get-value` with raw JSON in payload", payload=json.loads(result) if result else None
            )
        except Exception as e:
            return create_response(
                status_code=500,
                message=f"Error processing `/get-value`: {e!s}",
                payload=None,
            )


@app.post("/set-value")
async def set_value(payload: SetValuePayload) -> ResponseBody:
    """Set value to a specified protocol-specific endpoint from an AID submodel."""
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
            await asset_connector.set_value(reference, payload.value)
            return create_response(status_code=200, message="Successfully invoked `/set-value` with raw JSON in payload", payload=None)
        except Exception as e:
            return create_response(
                status_code=500,
                message=f"Error processing `/set-value`: {e!s}",
                payload=None,
            )


def start_app():
    """Function to start the FastAPI application."""
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8090"))
    uvicorn.run(app, host=host, port=port)
