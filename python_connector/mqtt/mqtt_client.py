"""MQTTConnector module for connecting to MQTT topics and caching messages.

Provides the MQTTConnector class for subscribing to topics, receiving messages,
and storing the latest payload for each topic.
"""

import logging
import ssl
from urllib.parse import urlparse

from aas_standard_parser.aid_parser import BasicAuthenticationDetails, IAuthenticationDetails
from paho.mqtt.client import Client

logger = logging.getLogger(__name__)


class MqttClient:
    """Connector for managing connections to MQTT topics."""

    base_url: str
    host: str
    port: int
    path: str

    def __init__(self, base_url: str, topics: list[str], auth: IAuthenticationDetails):
        """Initialize the MQTTConnector with broker host and port."""
        self.cache = {}
        for t in topics:
            self.cache[t] = None

        self.base_url = base_url
        self.host, self.port, self.path, use_tls = self._parse_url()

        self.client = Client(transport=self._detect_transport())

        if isinstance(auth, BasicAuthenticationDetails):
            self.client.username_pw_set(auth.user, auth.password)

        if use_tls:
            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, ca_certs=None)
            self.client.tls_insecure_set(True)

        if self._detect_transport() == "websockets" and self.path != "/":
            self.client.ws_set_options(path=self.path)

        self._is_connected = False

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _parse_url(self):
        """Extract host, port, and path from broker_url."""
        parsed = urlparse(self.base_url)

        # scheme like mqtt, mqtts, ws, wss
        scheme = parsed.scheme or "mqtt"

        # host
        host = parsed.hostname

        # port (fall back to defaults if missing)
        defaults = {"mqtt": 1883, "mqtts": 8883, "ws": 80, "wss": 443}
        port = parsed.port or defaults.get(scheme, 1883)

        # path (default to "/" if not given)
        path = parsed.path or "/" if "ws" in parsed.scheme else None

        # TLS required?
        use_tls = scheme in ("mqtts", "wss")

        return host, port, path, use_tls

    def _detect_transport(self):
        """Determine if plain MQTT or MQTT over WebSocket is needed."""
        if self.base_url.startswith("ws://") or self.base_url.startswith("wss://"):
            return "websockets"
        return "tcp"

    def connect(self):
        """Connect to the MQTT broker and subscribe to all topics.

        This method should be called after initializing the MQTTConnector.
        """
        try:
            logger.debug(f"Connecting to MQTT broker at '{self.base_url}:{self.port}'")
            self.client.connect(self.host, self.port, 60)
        except Exception as e:
            raise ConnectionError(f"Error connecting to MQTT broker at '{self.base_url}': {e}")

    def _on_connect(self, client, userdata, flags, rc):  # noqa: ARG002
        """Handle response from the server.

        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or userdata_set().
        :param flags: Response flags sent by the broker.
        :param rc: The connection result.
        """
        logger.info(f"Connected with result code {rc}")

        # Subscribe to all topics in self.topics
        if rc == 0:
            self._is_connected = True
            for topic in self.cache.keys():
                self.client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")

    def _on_message(self, client, userdata, message):  # noqa: ARG002
        """Handle incoming messages from subscribed topics.

        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or userdata_set().
        :param message: The message instance containing topic and payload.
        """
        topic = message.topic
        payload = message.payload.decode("utf-8")
        logger.info(f"Received message '{payload}' on topic '{topic}'")

        # Cache the message
        self.cache[topic] = payload

    def start_async(self):
        """Start the MQTT client loop in a separate thread for non-blocking operation.

        :return: True if the loop started successfully, False otherwise.
        """
        return self.client.loop_start()

    def stop(self):
        """Stop the MQTT client loop and disconnect from the broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def disconnect(self):
        """Disconnect from the MQTT broker gracefully."""
        self.client.disconnect()

    def dispose(self):
        """Clean up resources and disconnect from the MQTT broker.

        This method should be called when the connector is no longer needed
        to ensure proper cleanup of resources.
        """
        try:
            # Unsubscribe from all topics
            for topic in self.topics:
                self.client.unsubscribe(topic)

            # Stop the client loop and disconnect
            self.client.loop_stop()
            self.client.disconnect()

            # Clear internal state
            self.topics.clear()
            self.cache.clear()

        except (OSError, ConnectionError, RuntimeError) as e:
            logger.error(f"Error during disposal: {e}")

    def __enter__(self):
        """Context manager entry point.

        :return: The MQTTConnector instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - ensures proper cleanup.

        :param exc_type: Exception type if an exception was raised.
        :param exc_val: Exception value if an exception was raised.
        :param exc_tb: Exception traceback if an exception was raised.
        """
        self.dispose()

    def add_topics(self, topics):
        """Add topics to the MQTTConnector."""
        self.topics = topics

    def get_cached_value(self, topic):
        """Retrieve the cached value for a specific topic.

        :param topic: The topic to retrieve the cached value for.
        :return: The cached value if it exists, otherwise None.
        """
        return self.cache.get(topic, None)

    @property
    def is_connected(self):
        return self._is_connected

    def publish(self, topic: str, payload: str):
        """Publish a message to a specific topic.

        :param topic: The topic to publish the message to.
        :param payload: The message payload to be published.
        """
        self.client.publish(topic, payload)
