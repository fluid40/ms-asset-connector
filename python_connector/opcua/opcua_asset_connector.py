from basyx.aas.model import ModelReference, SubmodelElementCollection

from python_connector.core.asset_connector import IAssetConnector


class OpcuaAssetConnector(IAssetConnector):

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):  # noqa: D107
        self._aid_id = aid_id
        self._interface = interface_smc
        super().__init__(aid_id, interface_smc)

    def connect(self):
        # no connection needed -> just request values on demand
        pass

    def get_value(self, endpoint_reference: ModelReference) -> str:
        return super().get_value(endpoint_reference)

    def set_value(self, endpoint_reference: ModelReference, *args):
        super().set_value(endpoint_reference, *args)
