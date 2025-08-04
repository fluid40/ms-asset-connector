import asyncio

from basyx.aas.model import Identifier, Submodel

from core.aid_parser import AIDParser
from core.mqtt_connector import MQTTConnector
from core.reference_resolver import ReferenceResolver


class AssetConnector:
    """Class to connect to an asset using its AID."""

    _mqtt_connector: MQTTConnector = None

    def __init__(self, id: str):  # noqa: D107
        self.id = id

    def set_config(self, new_config: Submodel):
        self.aid = new_config
        aid_parser = AIDParser(new_config)
        mqtt_topics = aid_parser.get_mqtt_topics()

        self._mqtt_connector = MQTTConnector(aid_parser.base_url, mqtt_topics)
        self._mqtt_connector.start_async()

    def get_value(self, model_reference: dict) -> str:
        topic_name = ReferenceResolver.get_topic_by_reference(model_reference, self._mqtt_connector.topics)

        result: str = None
        if self._mqtt_connector is not None:
            result = self._mqtt_connector.get_cached_value(topic_name)

        return result


# class ConnectorStore:
#     """Store for AssetConnectors, allowing async access (thread-safe)."""

#     def __init__(self):  # noqa: D107
#         self._store: dict[str, AssetConnector] = {}
#         self._lock = asyncio.Lock()

#     async def set_connector(self, id: Identifier, aid: Submodel):
#         async with self._lock:
#             self._store[id] = AssetConnector(id, aid)

#     async def get_connector(self, id: Identifier) -> AssetConnector | None:
#         async with self._lock:
#             connector = self._store.get(id)
#             if not connector:
#                 raise KeyError(f"Connector with id {id} not found.")
#             return connector
