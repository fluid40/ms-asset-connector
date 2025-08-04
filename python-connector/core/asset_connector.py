"""Asset connector module for interfacing with assets via AID and MQTT."""
from basyx.aas.model import Submodel

from core.aid_parser import AIDParser
from core.mqtt_connector import MQTTConnector
from core.reference_resolver import ReferenceResolver


class AssetConnector:
    """Class to connect to an asset using its AID."""

    _mqtt_connector: MQTTConnector = None

    def __init__(self, id: str):  # noqa: D107
        self.id = id

    def set_config(self, new_config: Submodel):
        """Set the configuration for the asset connector."""
        self.aid = new_config
        aid_parser = AIDParser(new_config)
        mqtt_topics = aid_parser.get_mqtt_topics()

        self._mqtt_connector = MQTTConnector(aid_parser.base_url, mqtt_topics)
        self._mqtt_connector.start_async()

    def get_value(self, model_reference: dict) -> str:
        """Get the value for a specific model reference."""
        topic_name = ReferenceResolver.get_topic_by_reference(model_reference, self._mqtt_connector.topics)

        result: str = None
        if self._mqtt_connector is not None:
            result = self._mqtt_connector.get_cached_value(topic_name)

        return result
