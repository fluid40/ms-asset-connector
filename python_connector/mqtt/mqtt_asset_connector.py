"""Asset connector module for interfacing with assets via AID and MQTT."""

import json
import logging
from typing import List

from basyx.aas.model import ModelReference, SubmodelElementCollection
from core.aid_interface_parser import construct_idshort_path_from_reference
from core.asset_connector import IAssetConnector

from mqtt.mqtt_client import MqttClient

logger = logging.getLogger(__name__)


class MqttAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    _mqtt_client: MqttClient = None
    connected: bool = False

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):  # noqa: D107
        self._aid_id = aid_id
        self._interface = interface_smc
        self._connector_id = f"{aid_id}-{interface_smc.id_short}"
        super().__init__(aid_id, interface_smc)

    def connect(self):
        """Connect to the asset using the MQTT protocol."""
        try:
            topics = list(set([v["href"] for v in self._property_to_href_map.values()]))

            self.connected = self._connect_to_mqtt_topics(topics)
            logger.debug(f"Asset connector with id {self._connector_id} connected to MQTT asset with status: {self.connected}")
        except Exception as e:
            logger.error(f"Failed to connect MQTTConnector: {e}")
            self.connected = False

    def _connect_to_mqtt_topics(self, mqtt_topics: List[str]) -> bool:
        """Connect to the MQTT topics using a MQTT connector.

        :param mqtt_topics: The MQTT topics to connect to.
        :return: True if the connection was successful, False otherwise.
        """
        try:
            self._mqtt_client = MqttClient(self._base, mqtt_topics, self._auth)
            self._mqtt_client.connect()
            self._mqtt_client.start_async()
            return True
        except ConnectionError as ce:
            logger.error(f"MQTT protocol connection failed: {ce}.")
            return False

    def get_value(self, model_reference: ModelReference) -> str:
        """Get the value for a specific model reference.

        :param model_reference: The model reference to get the value for.
        :raises ConnectionError: If the connector is not connected.
        :return: The value for the specified model reference.
        """
        result: str = None
        if not self.connected:
            raise ConnectionError("AssetConnector is not connected.")
        if self._mqtt_client is not None:
            property_idshort_path = construct_idshort_path_from_reference(model_reference)
            topic_name = self._property_to_href_map[property_idshort_path]["href"]
            logger.debug(f"Getting value for property path {property_idshort_path}.")

            keys = self._property_to_href_map[property_idshort_path]["keys"]
            value_in_payload = self._mqtt_client.get_cached_value(topic_name)
            if value_in_payload is None:
                return None

            # using the keys of the potentially nested properties, dive into the complex JSON object (MQTT payload)
            # to retrieve the requested value
            for k in keys:
                value_in_payload = json.dumps(json.loads(value_in_payload)[k])

            result = value_in_payload

        return result
