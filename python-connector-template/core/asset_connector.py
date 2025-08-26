# TODO: change to AasCore if required
from basyx.aas.model import SubmodelElementCollection, Reference, ModelReference


class IAssetConnector:

    def __init__(self, aid_id: str, interface_smc: SubmodelElementCollection):
        self.aid_id = aid_id
        self.interface = interface_smc

    def connect(self):
        pass

    def get_value(self, endpoint_reference: ModelReference) -> str:
        pass

    def set_value(self, endpoint_reference: ModelReference, *args):
        pass

    def do_action(self, endpoint_reference: ModelReference, *args):
        pass
