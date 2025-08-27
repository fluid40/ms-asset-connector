"""Asset connector module for interfacing with assets via AID and MQTT."""
import json
from typing import List

from basyx.aas.model import ModelReference, Submodel, SubmodelElementCollection

from core.aid_interface_parser import AidInterfaceParser, construct_idshort_path_from_reference
from core.asset_connector import IAssetConnector
from mqtt.mqtt_client import MqttClient
from core.reference_resolver import ReferenceResolver


class MqttAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    _mqtt_client: MqttClient = None
    connected: bool = False

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):  # noqa: D107
        self._aid_id = aid_id
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    def connect(self):
        try:
            topics = list(set([v["href"] for v in self._property_to_href_map.values()]))

            self.connected = self._connect_to_mqtt_topics(topics)
        except Exception as e:
            print(f"Failed to connect MQTTConnector: {e}")
            self.connected = False

    def _connect_to_mqtt_topics(self, mqtt_topics: List[str]) -> bool:
        """Connect to the MQTT topics using a MQTT connector.

        :param base_url: The base URL for the MQTT broker.
        :param mqtt_topics: A dictionary of MQTT topics to subscribe to.
        :param use_websocket: Whether to use WebSocket for the connection.
        """
        try:
            self._mqtt_client = MqttClient(self._base, mqtt_topics)
            self._mqtt_client.connect()
            self._mqtt_client.start_async()
            return True
        except ConnectionError as ce:
            print(f"MQTT protocol connection failed: {ce}.")
            return False

    def get_value(self, model_reference: ModelReference) -> str:
        """Get the value for a specific model reference."""
        result: str = None
        if not self.connected:
            raise ConnectionError("AssetConnector is not connected.")
        if self._mqtt_client is not None:
            property_idshort_path = construct_idshort_path_from_reference(model_reference)
            topic_name = self._property_to_href_map[property_idshort_path]["href"]

            keys = self._property_to_href_map[property_idshort_path]["keys"]
            value_in_payload = self._mqtt_client.get_cached_value(topic_name)
            for k in keys:
                value_in_payload = json.dumps(json.loads(value_in_payload)[k])

            result = value_in_payload

        return result
