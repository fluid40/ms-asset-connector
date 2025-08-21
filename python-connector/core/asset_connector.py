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

    def set_config(self, new_aid: Submodel):
        """Set (or overwrite) the configuration for the asset connector.

        :param new_aid: The new AID to use for the connection.
        """
        self.aid = new_aid

        try:
            aid_parser = AIDParser(new_aid)
            mqtt_topics: dict[str, str] = aid_parser.get_mqtt_topic_map()
            base_url: str = aid_parser.get_mqtt_base_url()
            use_websocket_connection: bool = aid_parser.uses_websocket_interface()
            connection_success: bool = self._connect_to_mqtt_topics(base_url, mqtt_topics, use_websocket_connection)

            if not connection_success and not use_websocket_connection:
                print("Check for MQTT interface using Websocket as fallback.")
                mqtt_topics = aid_parser.get_mqtt_topic_map(fallback=True)
                base_url = aid_parser.get_mqtt_base_url(fallback=True)
                use_websocket_connection = aid_parser.uses_websocket_interface(fallback=True)
                connection_success = self._connect_to_mqtt_topics(base_url, mqtt_topics, use_websocket_connection)

            self.connected = connection_success
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

    def _connect_to_mqtt_topics(self, base_url: str, mqtt_topics: dict[str, str], use_websocket: bool) -> bool:
        """Connect to the MQTT topics using a MQTT connector.

        :param base_url: The base URL for the MQTT broker.
        :param mqtt_topics: A dictionary of MQTT topics to subscribe to.
        :param use_websocket: Whether to use WebSocket for the connection.
        """
        try:
            self._mqtt_connector = MQTTConnector(base_url, mqtt_topics, use_websocket)
            self._mqtt_connector.connect()
            self._mqtt_connector.start_async()
            return True
        except ConnectionError as ce:
            print(f"MQTT protocol connection failed: {ce}.")
            return False
