import opcua
from basyx.aas.model import ModelReference, SubmodelElementCollection

from python_connector.core.asset_connector import IAssetConnector


class OpcuaAssetConnector(IAssetConnector):

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self._aid_id = aid_id
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    def connect(self):
        self._client = opcua.Client(self._base)

        # TODO: set based on self._auth
        # self._client.set_user()
        # self._client.set_password()

        self._client.connect()

    def get_value(self, endpoint_reference: ModelReference) -> str:
        return super().get_value(endpoint_reference)

    def set_value(self, endpoint_reference: ModelReference, *args):
        super().set_value(endpoint_reference, *args)
