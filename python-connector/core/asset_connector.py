"""Asset connector module for interfacing with assets via AID and MQTT."""
from basyx.aas.model import ModelReference, Submodel

from core.aid_parser import AIDParser
from core.mqtt_connector import MQTTConnector
from core.reference_resolver import ReferenceResolver


class AssetConnector:
    """Class to connect to an asset using its AID."""

    _mqtt_connector: MQTTConnector = None
    connected: bool = False

    def __init__(self, id: str):  # noqa: D107
        self.id = id
        self.connected = False

    def set_config(self, new_config: Submodel):
        """Set the configuration for the asset connector."""
        self.aid = new_config
        aid_parser = AIDParser(new_config)
        mqtt_topics: dict[str, str] = aid_parser.get_mqtt_topics()
        base_url: str = aid_parser.get_base_url()
        try:
            self._mqtt_connector = MQTTConnector(base_url, mqtt_topics, aid_parser.has_websocket_interface())
            self._mqtt_connector.connect()
            self._mqtt_connector.start_async()
            self.connected = True
        except ConnectionError as ce:
            print(f"MQTT protocol connection failed: {ce}.")
            # TODO
        except Exception as e:
            print(f"Failed to connect MQTTConnector: {e}")
            self.connected = False

    def get_value(self, model_reference: ModelReference) -> str:
        """Get the value for a specific model reference."""
        topic_name = ReferenceResolver.get_topic_by_reference(model_reference, self._mqtt_connector.topics)

        result: str = None
        if not self.connected:
            raise ConnectionError("AssetConnector is not connected.")
        if self._mqtt_connector is not None:
            result = self._mqtt_connector.get_cached_value(topic_name)

        return result
