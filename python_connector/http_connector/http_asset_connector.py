"""Asset connector module for interfacing with assets via AID and http."""

import json
from typing import List, Optional

import requests
from aas_standard_parser.aid_parser import HttpProtocolBinding
from aas_standard_parser.reference_helpers import construct_idshort_path_from_reference
from basyx.aas.model import (
    ExternalReference,
    Key,
    KeyTypes,
    ModelReference,
    SubmodelElementCollection,
)

from python_connector.core.asset_connector import IAssetConnector


class HttpAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    property_cache: List

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        super().__init__(aid_id, interface_smc)
        self.is_connected = True
        self.property_cache = []

    async def get_value(self, model_reference: ModelReference) -> Optional[str]:
        """Get the value for a specific model reference."""

        property_idshort_path = construct_idshort_path_from_reference(model_reference)
        url_resource = self._parsed_properties[property_idshort_path].href
        keys = self._parsed_properties[property_idshort_path].keys
        protocol_binding: HttpProtocolBinding = self._parsed_properties[property_idshort_path].protocol_binding
        http_method = protocol_binding.method_name
        http_headers = protocol_binding.headers

        match http_method:
            case "GET":
                response = requests.get(self.base + url_resource, headers=http_headers)
            case method:
                raise ValueError(f"http method {method} not implemented.")
        response.raise_for_status()
        value_in_payload = response.text

        if value_in_payload is None:
            return None

        # using the keys of the potentially nested properties, dive into the complex JSON object (MQTT payload)
        # to retrieve the requested value
        for k in keys:
            value_in_payload = json.dumps(json.loads(value_in_payload)[k])

        result = str(value_in_payload)
        return result
