from aas_standard_parser import AIDParser
from aas_standard_parser.aid_parser import IAuthenticationDetails
from basyx.aas.model import ModelReference, SubmodelElementCollection


class IAssetConnector:
    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self._aid_id = aid_id
        self._interface = interface_smc

        self._parse_aid_interface()

    def _parse_aid_interface(self):
        # extract the base url
        aid_parser = AIDParser()
        try:
            self._base = aid_parser.get_base_url_from_interface(self._interface)
            self._property_to_href_map = aid_parser.create_property_to_href_map(self._interface)
            self._auth: IAuthenticationDetails = aid_parser.parse_security(self._interface)
        except ValueError as e:
            print(f"Error parsing aid interface: {e}")

    async def connect(self):
        pass

    async def get_value(self, endpoint_reference: ModelReference) -> str | None:
        pass

    async def set_value(self, endpoint_reference: ModelReference, *args):
        pass

    async def do_action(self, endpoint_reference: ModelReference, *args):
        pass
