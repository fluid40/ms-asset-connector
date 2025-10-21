from aas_standard_parser import AIDParser
from aas_standard_parser.aid_parser import IAuthenticationDetails
from basyx.aas.model import ModelReference, SubmodelElementCollection


class IAssetConnector:
    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self._aid_id = aid_id
        self._interface = interface_smc

        if not self._parse_aid_interface():
            raise ValueError("Failed to parse AID interface.")

    def _parse_aid_interface(self) -> bool:
        # extract the base url
        aid_parser = AIDParser()
        try:
            self._base = aid_parser.parse_base(self._interface)
            self._property_to_href_map = aid_parser.parse_properties(self._interface)
            self._auth: IAuthenticationDetails = aid_parser.parse_security(self._interface)
        except ValueError as e:
            print(f"Error parsing aid interface: {e}")
            return False

        return True

    async def connect(self):
        pass

    async def get_value(self, endpoint_reference: ModelReference) -> str | None:
        pass

    async def set_value(self, endpoint_reference: ModelReference, *args):
        pass

    async def do_action(self, endpoint_reference: ModelReference, *args):
        pass
