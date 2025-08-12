"""MQTTConnector module for connecting to MQTT topics and caching messages.

Provides the MQTTConnector class for subscribing to topics, receiving messages,
and storing the latest payload for each topic.
"""

import os
from urllib.parse import ParseResult, urlparse

from dotenv import load_dotenv
from paho.mqtt.client import Client


class MQTTConnector:
    """Connector for managing connections to MQTT topics."""

    def __init__(self, base_url: str, topics: dict[str, str]):
        """Initialize the MQTTConnector with broker host and port.

        :param broker_host: The hostname or IP address of the MQTT broker.
        :param broker_port: The port number of the MQTT broker.
        """
        load_dotenv()
        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topics: dict[str, str] = topics
        self.cache = {}

        # Load credentials from environment variables
        mqtt_username = os.getenv("MQTT_USERNAME")
        mqtt_password = os.getenv("MQTT_PASSWORD")
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)

        parsed_mqtt_url: ParseResult = urlparse(base_url)
        self.broker_host = parsed_mqtt_url.hostname
        self.broker_port = parsed_mqtt_url.port if parsed_mqtt_url.port else 1883

        # Note: start() method should be called manually after initialization
        # to avoid blocking in __init__

    def connect(self):
        """Connect to the MQTT broker and subscribe to all topics.

        This method should be called after initializing the MQTTConnector.
        """
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
        except Exception as e:
            raise ConnectionError(f"Error connecting to MQTT broker at {self.broker_host}:{self.broker_port}: {e}")

    def on_connect(self, client, userdata, flags, rc):  # noqa: ARG002
        """Handle response from the server.

        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or userdata_set().
        :param flags: Response flags sent by the broker.
        :param rc: The connection result.
        """
        print(f"Connected with result code {rc}")

        # Subscribe to all topics in self.topics
        for topic in self.topics.values():
            self.client.subscribe(topic)

    def on_message(self, client, userdata, message):  # noqa: ARG002
        """Handle incoming messages from subscribed topics.

        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or userdata_set().
        :param message: The message instance containing topic and payload.
        """
        topic = message.topic
        payload = message.payload.decode("utf-8")
        print(f"Received message '{payload}' on topic '{topic}'")

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
            print(f"Error during disposal: {e}")

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

    def add_topics(self, topics_dict):
        """Add topics to the MQTTConnector."""
        self.topics.update(topics_dict)



    def get_cached_value(self, topic):
        """Retrieve the cached value for a specific topic.

        :param topic: The topic to retrieve the cached value for.
        :return: The cached value if it exists, otherwise None.
        """
        return self.cache.get(topic, None)

class WebSocketMQTTConnector(MQTTConnector):
    """MQTTConnector subclass using WebSocket transport."""

    def __init__(self, base_url: str, topics: dict[str, str]):  # noqa: D107
        super().__init__(base_url, topics)
        self.client = Client(transport="websockets")
