"""Asset connector module for interfacing with assets via AID and http."""

import json
from typing import List, Optional

from basyx.aas.model import (
    ModelReference,
    Key,
    KeyTypes,
    SubmodelElementCollection,
    ExternalReference,
)

from python_connector.core.asset_connector import IAssetConnector
import requests


class HttpAssetConnector(IAssetConnector):
    """Class to connect to an asset using its AID."""

    property_cache: List

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        super().__init__(aid_id, interface_smc)
        self.property_cache = []

    async def get_value(self, model_reference: ModelReference) -> Optional[str]:
        """Get the value for a specific model reference."""
        result: Optional[str] = None
        # Get the requested property using the model reference. The AID SM and Interface SMC
        # references are not needed.
        property = self._interface.get_referable(
            map(lambda k: k.value, model_reference.key[2:])
        )
        rootProperty = property
        property_smc_semantic_id = ExternalReference(
            (
                Key(
                    type_=KeyTypes.GLOBAL_REFERENCE,
                    value="https://www.w3.org/2019/wot/td#PropertyAffordance",
                ),
            )
        )
        keys = []
        while rootProperty.parent.semantic_id != property_smc_semantic_id:  # type: ignore
            keys.insert(0, rootProperty.id_short)  # type: ignore
            rootProperty = rootProperty.parent  # type: ignore

        url = self._base + rootProperty.get_referable(["forms", "href"]).value  # type: ignore
        try:
            headers = {
                h.get_referable("htv_fieldName")
                .value: h.get_referable("htv_fieldValue")
                .value
                for h in rootProperty.get_referable(["forms", "htv_headers"]).value  # type: ignore
            }
        except KeyError:
            headers = {}
        match rootProperty.get_referable(["forms", "htv_methodName"]).value:  # type: ignore
            case "GET":
                response = requests.get(url, headers=headers)
            case method:
                raise ValueError(f"http method {method} not implemented.")
        response.raise_for_status()
        result = response.text

        # using the keys of the potentially nested properties, dive into the complex JSON object
        # to retrieve the requested value
        for k in keys:
            result = json.dumps(json.loads(result)[k])  # type: ignore

        return result
