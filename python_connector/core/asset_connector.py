import logging

from aas_standard_parser import AIDParser
from aas_standard_parser.aid_parser import IAuthenticationDetails
from basyx.aas.model import ModelReference, SubmodelElementCollection

logger = logging.getLogger(__name__)


class IAssetConnector:
    """Interface for asset connectors.
    It serves as the base class for any protocol-specific implementations and provides common functionality.
    """

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        """Initialize the AssetConnector with AID ID and interface submodel collection.

        :param aid_id: The ID of the AID submodel.
        :param interface_smc: A SubmodelElementCollection inside the AID submodel specifying the asset interface.
        """
        self._aid_id = aid_id
        self._interface = interface_smc
        self.is_connected = False

        if not self._parse_aid_interface():
            raise ValueError("Failed to parse AID interface.")

    def _parse_aid_interface(self) -> bool:
        """Parse the asset interface definition.
        Extracts authentication details, base address, and property endpoints for connecting to the asset.
        Stores the extracted information in self._auth, `self.base`, and `self._parsed_properties`."""
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
        """Get value from the asset for the specified endpoint reference.

        :param endpoint_reference: A reference pointing to an endpoint inside the AID interface specification.
        """

    async def set_value(self, endpoint_reference: ModelReference, *args):
        """Set a value on the asset via the specified endpoint.

        :param endpoint_reference: A reference pointing to an endpoint inside the AID interface specification.
        :param args: Key-value pairs to be written to the endpoint.
        """

    async def do_action(self, endpoint_reference: ModelReference, *args):
        """Invoke action on the asset for the specified endpoint reference.
        Not implemented yet.

        :param endpoint_reference: A reference pointing to an endpoint inside the AID interface specification.
        :param args: Key-value pairs as parameters to the invoked action.
        """
