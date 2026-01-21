import logging

from aas_standard_parser import AIDParser
from aas_standard_parser.aid_parser import IAuthenticationDetails
from basyx.aas.model import ModelReference, SubmodelElementCollection

logger = logging.getLogger(__name__)


class IAssetConnector:
    """Interface for asset connectors."""

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        """Initialize the AssetConnector with AID ID and interface submodel collection."""
        self._aid_id = aid_id
        self._interface = interface_smc
        self.is_connected = False

        if not self._parse_aid_interface():
            raise ValueError("Failed to parse AID interface.")

    def _parse_aid_interface(self) -> bool:
        # extract the base url
        aid_parser = AIDParser()
        try:
            self.base = aid_parser.parse_base(self._interface)
            self._parsed_properties = aid_parser.parse_properties(self._interface)
            self._auth: IAuthenticationDetails = aid_parser.parse_security(self._interface)
        except ValueError as e:
            logger.error(f"Error parsing aid interface: {e}")
            return False

        return True

    async def connect(self):
        """Connect to the asset."""

    async def get_value(self, endpoint_reference: ModelReference) -> str | None:
        """Get value from the asset for the specified endpoint reference."""

    async def set_value(self, endpoint_reference: ModelReference, *args):
        """Set value on the asset for the specified endpoint reference."""

    async def do_action(self, endpoint_reference: ModelReference, *args):
        """Invoke action on the asset for the specified endpoint reference."""
