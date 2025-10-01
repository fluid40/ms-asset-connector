import json

from opcua import Client
from basyx.aas.model import ModelReference, SubmodelElementCollection

from python_connector.core.aid_interface_parser import construct_idshort_path_from_reference
from python_connector.core.asset_connector import IAssetConnector


class OpcuaAssetConnector(IAssetConnector):

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self._client = None
        self._is_connected = False
        self._aid_id = aid_id
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    async def connect(self):
        try:
            self._client = Client(self._base)
            self._client.connect()
            self._is_connected = True
        except Exception as e:
            print(e)

    async def get_value(self, endpoint_reference: ModelReference) -> str | None:
        """Get the value for a specific model reference."""

        property_idshort_path = construct_idshort_path_from_reference(endpoint_reference)
        node_id = self._property_to_href_map[property_idshort_path]["href"]
        keys = self._property_to_href_map[property_idshort_path]["keys"]

        if not self._is_connected:
            raise ConnectionError("AssetConnector is not connected.")

        if self._client is None:
            raise ConnectionError("OPCUA Client not properly initialized.")

        node = self._client.get_node(node_id)
        value_in_payload = node.get_value()

        if value_in_payload is None:
            return None

        # using the keys of the potentially nested properties, dive into the complex JSON object (MQTT payload)
        # to retrieve the requested value
        for k in keys:
            value_in_payload = json.dumps(json.loads(value_in_payload)[k])

        result = str(value_in_payload)
        return result
