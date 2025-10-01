"""Asset connector module for interfacing with assets via AID and MQTT."""
import json
from typing import List

from basyx.aas.model import ModelReference, SubmodelElementCollection

from python_connector.core.aid_interface_parser import construct_idshort_path_from_reference
from python_connector.core.asset_connector import IAssetConnector
from python_connector.mqtt.mqtt_client import MqttClient



class MqttAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    _mqtt_client: MqttClient = None

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):  # noqa: D107
        self._aid_id = aid_id
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    async def connect(self):
        try:
            topics = list(set([v["href"] for v in self._property_to_href_map.values()]))
            self._connect_to_mqtt_topics(topics)
        except Exception as e:
            print(f"Failed to connect MQTTConnector: {e}")

    def _connect_to_mqtt_topics(self, mqtt_topics: List[str]):
        """Connect to the MQTT topics using a MQTT connector.

        :param mqtt_topics: A dictionary of MQTT topics to subscribe to.
        """
        try:
            self._mqtt_client = MqttClient(self._base, mqtt_topics, self._auth)
            self._mqtt_client.connect()
            self._mqtt_client.start_async()
        except ConnectionError as ce:
            print(f"MQTT protocol connection failed: {ce}.")

    async def get_value(self, model_reference: ModelReference) -> str | None:
        """Get the value for a specific model reference."""

        if not self._mqtt_client.is_connected:
            raise ConnectionError("AssetConnector is not connected.")

        if self._mqtt_client is None:
            raise ConnectionError("MQTT Client not properly initialized.")

        property_idshort_path = construct_idshort_path_from_reference(model_reference)
        topic_name = self._property_to_href_map[property_idshort_path]["href"]

        keys = self._property_to_href_map[property_idshort_path]["keys"]
        value_in_payload = self._mqtt_client.get_cached_value(topic_name)

        if value_in_payload is None:
            return None

        # using the keys of the potentially nested properties, dive into the complex JSON object (MQTT payload)
        # to retrieve the requested value
        for k in keys:
            value_in_payload = json.dumps(json.loads(value_in_payload)[k])

        result = str(value_in_payload)
        return result
