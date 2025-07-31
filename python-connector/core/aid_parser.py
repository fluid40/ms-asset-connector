"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""

from basyx.aas import model
from basyx.aas.model import NamespaceSet, Reference, Submodel, SubmodelElement, SubmodelElementCollection
from basyx.aas.util import traversal

SEMANTIC_ID_INTERFACE: str = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface"
SEMANTIC_ID_MQTT: str = "http://www.w3.org/2011/mqtt"
class AIDParser:
    """A class to handle parsing of AID Submodels and connecting to MQTT topics."""

    _aid_sm: Submodel
    _mqtt_interface: SubmodelElementCollection = None
    _interaction_properties: list = None


    def __init__(self, aid_sm: Submodel):
        """Initialize the AIDParser with a JSON representation of an AID Submodel.

        Extracts the MQTT interface collection and all Interactionmetadata.property elements.
        """
        self._aid_sm = aid_sm

        mqtt_interface: SubmodelElementCollection = find_by_semantic_id(aid_sm.submodel_element, SEMANTIC_ID_INTERFACE)
        if mqtt_interface is None:
            raise ValueError("MQTT interface description not found in AID Submodel.")
        self._mqtt_interface = mqtt_interface
 
        interaction_metadata: SubmodelElementCollection = find_by_supplemental_semantic_id(
            self._mqtt_interface.value, SEMANTIC_ID_MQTT
        )
        if interaction_metadata is None:
            raise ValueError("InteractionMetadata SMC not found in MQTT interface description.")

        self._interaction_properties = self._loop_property_definitions(interaction_metadata)

    def _loop_property_definitions(self, interaction_metadata: SubmodelElementCollection):
        """
        Loop through the MQTT interface collection and find all Interactionmetadata.property elements.

        :param interaction_metadata: The Interactionmetadata collection object.
        :return: List of property elements found under Interactionmetadata.
        """
        mqtt_property_collection: SubmodelElementCollection = find_by_semantic_id(
            interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
        )
        # TODO


    def _find_topics(self):
        pass

def find_by_semantic_id(parent: NamespaceSet[SubmodelElement], semantic_id_value: str) -> SubmodelElement:
    """Find a SubmodelElement by its semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The semantic ID value to search for.
    :return: The found SubmodelElement, or None if not found.
    """
    reference: Reference = model.ExternalReference(
        [model.Key(
            type_= model.KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        )]
    )
    for element in parent:
        if element.semantic_id.__eq__(reference):
            return element
    return None

def find_by_supplemental_semantic_id(parent: NamespaceSet[SubmodelElement], semantic_id_value: str) -> SubmodelElement:
    """Find a SubmodelElement by its supplemental semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The supplemental semantic ID value to search for.
    :return: The found SubmodelElement, or None if not found.
    """
    reference: Reference = model.ExternalReference(
        [model.Key(
            type_= model.KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        )]
    )

    for element in parent:
        if element.supplemental_semantic_id.__eq__(reference):
            return element
    return None
