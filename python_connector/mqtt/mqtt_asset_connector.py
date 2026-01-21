"""Asset connector module for interfacing with assets via AID and MQTT."""

import json
import logging

from aas_standard_parser.reference_helpers import construct_id_short_path_from_reference
from basyx.aas.model import ModelReference, SubmodelElementCollection

from ..core.asset_connector import IAssetConnector
from .mqtt_client import MqttClient

logger = logging.getLogger(__name__)


class MqttAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    _mqtt_client: MqttClient = None

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):  # noqa: D107
        logger.debug(f"Initializing MQTTAssetConnector for AID '{aid_id}'")
        self._aid_id = aid_id
        self.is_connected = False
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    async def connect(self):
        """Connect to the MQTT broker and subscribe to relevant topics."""
        logger.info(f"Connecting to MQTT Asset for AID '{self._aid_id}'")
        try:
            topics = list({v.href for v in self._parsed_properties.values()})
            self.is_connected = self._connect_to_mqtt_topics(topics)
        except Exception as e:
            logger.error(f"Failed to connect to MQTT topics: {topics}. Error: {e}")
            raise ConnectionError(f"Failed to connect to MQTT topics: {topics}. Error: {e}") from e

    def _connect_to_mqtt_topics(self, mqtt_topics: list[str]) -> bool:
        """Connect to the MQTT topics using a MQTT connector.

        :param mqtt_topics: A dictionary of MQTT topics to subscribe to.
        """
        try:
            logger.info(f"Create MQTT client to '{self.base}'")
            self._mqtt_client = MqttClient(self.base, mqtt_topics, self._auth)
            logger.info(f"Subscribing to MQTT topics: {mqtt_topics}")
            self._mqtt_client.connect()
            self._mqtt_client.start_async()
            return True
        except ConnectionError as ce:
            logger.error(f"Failed to connect to MQTT topics: {mqtt_topics}. Error: {ce}")
            raise ConnectionError(f"Failed to connect to MQTT topics: {mqtt_topics}. Error: {ce}") from ce

        return False

    async def get_value(self, model_reference: ModelReference) -> str | None:
        """Get the value for a specific model reference."""
        # TODO: maybe try to use last cached value (if any) anyway
        if not self._mqtt_client.is_connected:
            raise ConnectionError("AssetConnector is not connected.")

        if self._mqtt_client is None:
            raise ConnectionError("MQTT Client not properly initialized.")

        property_idshort_path = construct_id_short_path_from_reference(model_reference)

        try:
            topic_name = self._parsed_properties[property_idshort_path].href
            keys = self._parsed_properties[property_idshort_path].keys
        except KeyError:
            raise KeyError(f"Property {property_idshort_path} not found.")

        value_in_payload = self._mqtt_client.get_cached_value(topic_name)

        if value_in_payload is None:
            return None

        # using the keys of the potentially nested properties, dive into the complex JSON object (MQTT payload)
        # to retrieve the requested value
        for k in keys:
            value_in_payload = json.dumps(json.loads(value_in_payload)[k])

        result = str(value_in_payload)
        return result

    async def set_value(self, endpoint_reference: ModelReference, value: dict[str]):
        """Set the value for a specific model reference."""
        if not self._mqtt_client.is_connected:
            raise ConnectionError("AssetConnector is not connected.")

        if self._mqtt_client is None:
            raise ConnectionError("MQTT Client not properly initialized.")

        property_idshort_path = construct_id_short_path_from_reference(endpoint_reference)

        try:
            topic_name = self._property_to_href_map[property_idshort_path].href
        except KeyError:
            raise KeyError(f"Property {property_idshort_path} not found.")

        payload = json.dumps(value)
        self._mqtt_client.publish(topic_name, payload)
        print(f"Published to topic {topic_name} with payload {payload}")
