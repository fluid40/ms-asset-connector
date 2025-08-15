"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""

from collections.abc import Iterator
from typing import NamedTuple

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


class MQTTInterfaceDescription(NamedTuple):
    """Represents an MQTT interface configuration for a specific asset.

    :param interface_smc: The SubmodelElementCollection representing the MQTT interface.
    :param base_url: The base URL for the MQTT interface.
    :param websocket_connection: Whether this interface is using a WebSocket connection or not (default).
    """

    interface_smc: SubmodelElementCollection
    base_url: str
    websocket_connection: bool = False

class AIDParser:
    """A class to handle parsing of AID Submodels and connecting to MQTT topics."""

    _topics: dict[str, str] = {}

    _aid_sm: Submodel
    _mqtt_interfaces: list[MQTTInterfaceDescription]

    def __init__(self, aid_sm: Submodel):
        """Initialize the AIDParser with a JSON representation of an AID Submodel.

        Extracts the MQTT interface collection and all InteractionMetadata.property elements.
        """
        self._aid_sm = aid_sm

        mqtt_interfaces: list[SubmodelElementCollection] = self._find_mqtt_interfaces()
        if not mqtt_interfaces or mqtt_interfaces == []:
            raise ValueError("No MQTT interface description found in AID Submodel.")

        self._mqtt_interfaces = [
            MQTTInterfaceDescription(
                interface_smc=smc,
                base_url=self._get_base_url(smc),
                websocket_connection=self._uses_websocket(smc)
            )
            for smc in mqtt_interfaces
        ]
        print(f"Found {len(self._mqtt_interfaces)} MQTT interfaces in AID Submodel.")

    def _find_mqtt_interfaces(self) -> list[SubmodelElementCollection]:
        """Find all MQTT interface collections in the AID Submodel by semantic_id and supplemental_semantic_id.

        :return: A list of MQTT interface collections found, or an empty list if none are found.
        """
        interfaces: list[SubmodelElement] = find_all_by_semantic_id(
            self._aid_sm.submodel_element, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface"
        )

        return [interface for interface in interfaces if isinstance(interface, SubmodelElementCollection) and
                contains_supplemental_semantic_id(interface, "http://www.w3.org/2011/mqtt")] if interfaces else []


    def _get_base_url(self, mqtt_interface: SubmodelElementCollection) -> str:
        """Set the base URL for the MQTT interface from the EndpointMetadata SMC."""
        endpoint_metadata: SubmodelElementCollection = find_by_semantic_id(
            mqtt_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
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
        return base.value


    def get_mqtt_topics(self) -> dict[str, str]:
        """
        Loop through the MQTT interface collection and find all InteractionMetadata.property elements.

        # TODO: do not use the topics from the default mqtt_interface, but from the one that will be used at the end.

        :return: List of property elements found under InteractionMetadata.
        """
        default_mqtt_interface: MQTTInterfaceDescription = self._get_default_mqtt_interface_description()
        mqtt_property_collection: SubmodelElementCollection = self._get_mqtt_properties(default_mqtt_interface.interface_smc)

        property_definitions: list[SubmodelElementCollection] = [
            prop_def for prop_def in find_all_by_semantic_id(
                traversal.walk_submodel(mqtt_property_collection),
                "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
            )
            if isinstance(prop_def, SubmodelElementCollection) and
            find_by_semantic_id(prop_def.value, "https://www.w3.org/2019/wot/td#hasForm") is not None
        ]

        self._find_topics(property_definitions)
        return self._topics

    def get_base_url(self) -> str:
        """Return the base url used for the MQTT connection.

        :return: The base URL of the default MQTT interface.
        """
        default_mqtt_interface = self._get_default_mqtt_interface_description()

        return self._get_base_url(default_mqtt_interface.interface_smc)

    def has_websocket_interface(self) -> bool:
        """Check if the MQTT connection will be initialized using Websocket.

        :return: True if the default MQTT interface uses WebSocket, False otherwise.
        """
        return self._get_default_mqtt_interface_description().websocket_connection

    def _get_default_mqtt_interface_description(self) -> MQTTInterfaceDescription:
        """Get the default MQTT interface description from the list of MQTT interfaces.

        Default MQTT interface does not use Websocket. If no such interface is found, simply return the first one.

        :return: The default MQTT interface.
        """
        for interface in self._mqtt_interfaces:
            if not interface.websocket_connection:
                return interface
        return self._mqtt_interfaces[0] if len(self._mqtt_interfaces) > 0 else None

    def _get_mqtt_properties(self, default_mqtt_interface: SubmodelElementCollection) -> SubmodelElementCollection:
        """Get the MQTT properties from the InteractionMetadata SMC.

        :return: The SubmodelElementCollection containing MQTT properties.
        """
        interaction_metadata: SubmodelElementCollection = find_by_semantic_id(
            default_mqtt_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
        )
        if interaction_metadata is None:
            raise ValueError("InteractionMetadata SMC not found in MQTT interface description.")

        mqtt_property_collection: SubmodelElementCollection = find_by_semantic_id(
            interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
        )
        if mqtt_property_collection is None:
            raise ValueError("PropertyAffordance SMC not found in InteractionMetadata SMC.")
        if not isinstance(mqtt_property_collection, SubmodelElementCollection):
            raise TypeError("PropertyAffordance is not a SubmodelElementCollection type.")

        return mqtt_property_collection

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

    def _uses_websocket(self, mqtt_interface: SubmodelElementCollection) -> bool:
        """Check if the given MQTT interface uses a WebSocket connection by searching for the appropriate semantic ID.

        :param mqtt_interface: The MQTT interface to check.
        :return: True if the interface uses WebSocket, False otherwise.
        """
        return contains_supplemental_semantic_id(mqtt_interface, "https://www.rfc-editor.org/rfc/rfc6455")

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
    for element in parent:
        if contains_supplemental_semantic_id(element, semantic_id_value):
            return element
    return None

def contains_supplemental_semantic_id(element: SubmodelElement, semantic_id_value: str) -> bool:
    """Check if the element contains a specific supplemental semantic ID.

    :param element: The SubmodelElement to check.
    :param semantic_id_value: The supplemental semantic ID value to search for.
    :return: True if the element contains the supplemental semantic ID, False otherwise.
    """
    reference: Reference = ExternalReference(
        [Key(
            type_= KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        )]
    )
    return element.supplemental_semantic_id.__contains__(reference)
