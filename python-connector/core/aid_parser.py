"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""

from collections.abc import Iterator

from basyx.aas.model import (
    ExternalReference,
    Key,
    KeyTypes,
    NamespaceSet,
    Property,
    Reference,
    Submodel,
    SubmodelElement,
    SubmodelElementCollection,
)
from basyx.aas.util import traversal


class AIDParser:
    """A class to handle parsing of AID Submodels and connecting to MQTT topics."""

    topics: dict[str, str]

    _aid_sm: Submodel
    _mqtt_interface: SubmodelElementCollection = None
    _interaction_properties: list = None
    _base_url: str = ""


    def __init__(self, aid_sm: Submodel):
        """Initialize the AIDParser with a JSON representation of an AID Submodel.

        Extracts the MQTT interface collection and all Interactionmetadata.property elements.
        """
        self._aid_sm = aid_sm

        mqtt_interface: SubmodelElementCollection = self._find_mqtt_interface()
        if mqtt_interface is None:
            raise ValueError("MQTT interface description not found in AID Submodel.")
        self._mqtt_interface = mqtt_interface

        self._get_base_url()

        interaction_metadata: SubmodelElementCollection = find_by_semantic_id(
            self._mqtt_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
        )
        if interaction_metadata is None:
            raise ValueError("InteractionMetadata SMC not found in MQTT interface description.")

        self._interaction_properties = self._extract_topics(interaction_metadata)

    def _find_mqtt_interface(self) -> SubmodelElementCollection:
        """Find the MQTT interface collection in the AID Submodel by semantic_id and supplemental_semantic_id.

        :return: The MQTT interface collection if found, otherwise None.
        """
        interfaces: list[SubmodelElement] = find_all_by_semantic_id(
            self._aid_sm.submodel_element, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface"
        )

        mqtt_ref: Reference = ExternalReference(
            [Key(
                type_ = KeyTypes.GLOBAL_REFERENCE,
                value = "http://www.w3.org/2011/mqtt"
            )]
        )
        return next(interface for interface in interfaces if isinstance(interface, SubmodelElementCollection) and
                           interface.supplemental_semantic_id.__contains__(mqtt_ref)) if interfaces else None


    def _get_base_url(self):
        """Set the base URL for the MQTT interface from the EndpointMetadata SMC."""
        endpoint_metadata: SubmodelElementCollection = find_by_semantic_id(
            self._mqtt_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
        )
        if endpoint_metadata is None:
            raise ValueError("EndpointMetadata SMC not found in AID Submodel.")
        base: Property = find_by_semantic_id(
            endpoint_metadata.value, "https://www.w3.org/2019/wot/td#base"
        )
        if base is None:
            raise ValueError("BaseUrl Property not found in EndpointMetadata SMC.")
        if not isinstance(base, Property):
            raise TypeError("BaseUrl is not a Property type.")
        self._base_url = base.value


    def _extract_topics(self, interaction_metadata: SubmodelElementCollection):
        """
        Loop through the MQTT interface collection and find all Interactionmetadata.property elements.

        :param interaction_metadata: The Interactionmetadata collection object.
        :return: List of property elements found under Interactionmetadata.
        """
        mqtt_property_collection: SubmodelElementCollection = find_by_semantic_id(
            interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
        )
        if mqtt_property_collection is None:
            raise ValueError("PropertyAffordance SMC not found in InteractionMetadata SMC.")
        if not isinstance(mqtt_property_collection, SubmodelElementCollection):
            raise TypeError("PropertyAffordance is not a SubmodelElementCollection type.")

        property_definitions: list[SubmodelElementCollection] = [
            prop_def for prop_def in find_all_by_semantic_id(
                traversal.walk_submodel(mqtt_property_collection),
                "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
            )
            if isinstance(prop_def, SubmodelElementCollection) and
            find_by_semantic_id(prop_def.value, "https://www.w3.org/2019/wot/td#hasForm") is not None
        ]

        self._find_topics(property_definitions)

    def _find_topics(self, property_definitions: list[SubmodelElementCollection]):
        for prop_def in property_definitions:
            forms = find_by_semantic_id(
                prop_def.value, "https://www.w3.org/2019/wot/td#hasForm"
            )

            target_href = find_by_semantic_id(
                forms.value, "https://www.w3.org/2019/wot/hypermedia#hasTarget"
            )

            if target_href is None:
                raise ValueError("TargetHref not found in Form SMC.")
            if not isinstance(target_href, Property):
                raise TypeError("TargetHref is not a Property type.")

            self._topics[prop_def.id_short] = target_href.value

        

def find_all_by_semantic_id(parent: Iterator[SubmodelElement], semantic_id_value: str) -> list[SubmodelElement]:
    """Find all SubmodelElements having a specific Semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The semantic ID value to search for.
    :return: The found SubmodelElement(s) or an empty list if not found.
    """
    reference: Reference = ExternalReference(
        [Key(
            type_= KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        )]
    )
    found_elements: list[SubmodelElement] = [
        element for element in parent if element.semantic_id.__eq__(reference)
    ]
    return found_elements

def find_by_semantic_id(parent: NamespaceSet[SubmodelElement], semantic_id_value: str) -> SubmodelElement:
    """Find a SubmodelElement by its semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The semantic ID value to search for.
    :return: The first found SubmodelElement, or None if not found.
    """
    reference: Reference = ExternalReference(
        [Key(
            type_= KeyTypes.GLOBAL_REFERENCE,
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
    :return: The first found SubmodelElement, or None if not found.
    """
    reference: Reference = ExternalReference(
        [Key(
            type_= KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        )]
    )

    for element in parent:
        if element.supplemental_semantic_id.__eq__(reference):
            return element
    return None
