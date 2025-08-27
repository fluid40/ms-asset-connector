# TODO: change to AasCore if required
from typing import Dict

from basyx.aas.model import SubmodelElementCollection, ModelReference

from core.aid_interface_parser import get_base_url_from_interface, create_property_to_href_map


class IAssetConnector:

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self._aid_id = aid_id
        self._interface = interface_smc

        self._parse_aid_interface()

    def _parse_aid_interface(self):
        # extract the base url
        self._base = get_base_url_from_interface(self._interface)
        self._property_to_href_map = create_property_to_href_map(self._interface)

    def connect(self):
        pass

    def get_value(self, endpoint_reference: ModelReference) -> str:
        pass

    def set_value(self, endpoint_reference: ModelReference, *args):
        pass

    def do_action(self, endpoint_reference: ModelReference, *args):
        pass
