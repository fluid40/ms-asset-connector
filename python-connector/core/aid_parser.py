"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""

from collections.abc import Iterator
from basyx.aas.model import Submodel, NamespaceSet, SubmodelElement, Reference
from basyx.aas.util import traversal


SEMANTIC_ID_INTERFACE: str = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface"
SEMANTIC_ID_MQTT: str = "http://www.w3.org/2011/mqtt"
class AIDParser:
    """A class to handle parsing of AID Submodels and connecting to MQTT topics."""

    _aid_sm: Submodel
    _mqtt_interface: object = None
    _interaction_properties: list = None


    def __init__(self, aid_sm: Submodel):
        """Initialize the AIDParser with a JSON representation of an AID Submodel.

        Extracts the MQTT interface collection and all Interactionmetadata.property elements.
        """
        self._aid_sm = aid_sm

        interface_smes = [sme for sme in aid_sm.submodel_element
                          if sme.semantic_id and sme.semantic_id.keys[0].value == SEMANTIC_ID_INTERFACE]
        self._mqtt_interface = self._find_mqtt_interface_description(aid_sm.submodel_element)
        self._interaction_properties = self._loop_property_definitions(self._mqtt_interface)


    def _find_mqtt_interface_description(self, submodel_elements: NamespaceSet[SubmodelElement]) -> SubmodelElement:
        """
        Find the MQTT interface collection in the AID Submodel.

        :param aid_sm: The AID Submodel to search.
        :return: The MQTT interface collection object, or None if not found.
        """
        # TODO find MQTT interface in submodel
        # TODO loop interaction metadata and map idShort/ key to topic links
        # # Assuming the MQTT interface is a SubmodelElementCollection with idShort 'MQTT'
        smes: Iterator[SubmodelElement] = traversal.walk_semantic_ids_recursive(self._aid_sm)
        mqtt_interface = next(
            (sme for sme in smes
             if sme.semantic_id and sme.semantic_id.keys[0].value == SEMANTIC_ID_INTERFACE),
            None
        )
        # mqtt_interface = next(
        #     (
        #         sme for sme in submodel_elements
        #         if sme.semantic_id
        #         and sme.semantic_id.keys[0].value == semantic_id_val_interface
        #         # and any(
        #         #     sup_key.value == semantic_id_val_mqtt
        #         #     for ref in getattr(sme, "supplemental_semantic_ids", [])
        #         #     for sup_key in ref.keys
        #         # )
        #     ),
        #     None
        # )
        return None #mqtt_interface

    def _loop_property_definitions(self, mqtt_interface):
        """
        Loop through the MQTT interface collection and find all Interactionmetadata.property elements.

        :param mqtt_interface: The MQTT interface collection object.
        :return: List of property elements found under Interactionmetadata.
        """
        properties = []
        if mqtt_interface is None:
            return properties
        for elem in getattr(mqtt_interface, 'value', []):
            if getattr(elem, 'id_short', '').lower() == 'interactionmetadata' and elem.model_type == 'SubmodelElementCollection':
                for subelem in getattr(elem, 'value', []):
                    if subelem.model_type == 'Property':
                        properties.append(subelem)
        return properties

    def _find_topics(self):
        pass