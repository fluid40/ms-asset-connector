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
    """A class to handle parsing of AID Submodels and connecting to MQTT topics.

    It extracts the MQTT topic information from the AID Submodel as well as the base url of the MQTT broker.
    All MQTT interface configurations are stored in a list of MQTTInterfaceDescriptions.
    """

    _mqtt_interface_descriptions: list[MQTTInterfaceDescription]
    _default_mqtt_interface: MQTTInterfaceDescription = None
    _fallback_mqtt_interface: MQTTInterfaceDescription = None
    _topic_map: dict[str, str] = {}

    def __init__(self, aid_sm: Submodel):
        """Initialize the AIDParser with a JSON representation of an AID Submodel.

        Extract all MQTT interface collections and find the contained MQTT topics using the default interface.
        """
        mqtt_interfaces: list[SubmodelElementCollection] = self._find_all_mqtt_interfaces(aid_sm)
        if mqtt_interfaces == []:
            print("No MQTT interface description found in AID Submodel.")

        self._mqtt_interface_descriptions = [
            MQTTInterfaceDescription(
                interface_smc=smc,
                base_url=self._get_base_url_from_interface(smc),
                websocket_connection=self._uses_websocket(smc)
            )
            for smc in mqtt_interfaces
        ]
        print(f"Found {len(self._mqtt_interface_descriptions)} MQTT interfaces in AID Submodel.")
        self._default_mqtt_interface = self._get_default_mqtt_interface_description()
        self._fallback_mqtt_interface = self._get_fallback_mqtt_interface_description()
        self._create_topic_map(self._default_mqtt_interface.interface_smc)

    def _find_all_mqtt_interfaces(self, aid_sm: Submodel) -> list[SubmodelElementCollection]:
        """Find all MQTT interface collections in the AID Submodel by semantic_id and supplemental_semantic_id.

        :return: A list of MQTT interface SubmodelElementCollections or an empty list if none are found.
        """
        interfaces: list[SubmodelElement] = find_all_by_semantic_id(
            aid_sm.submodel_element, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface"
        )

        return [interface for interface in interfaces if isinstance(interface, SubmodelElementCollection) and
                contains_supplemental_semantic_id(interface, "http://www.w3.org/2011/mqtt")] if interfaces else []

    def _get_base_url_from_interface(self, mqtt_interface: SubmodelElementCollection) -> str:
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
        return base.value

    def _create_topic_map(self, mqtt_interface: SubmodelElementCollection):
        """Find all MQTT topics by their property definitions in the MQTT interface SMC and create a new topic Map.

        The topic Map is a dictionary of the Topic Name (IdShort of the Property Definition) and the MQTT topic link.

        :param mqtt_interface: The MQTT interface SubmodelElementCollection to use.
        """
        print(f"Creating topic map for MQTT interface {mqtt_interface.id_short}.")
        mqtt_property_collection: SubmodelElementCollection = self._get_mqtt_properties(mqtt_interface)
        if not mqtt_property_collection:
            print(f"No MQTT properties found in InteractionMetadata of MQTT Interface {mqtt_interface.id_short}.")
            return

        property_definitions: list[SubmodelElementCollection] = [
            prop_def for prop_def in find_all_by_semantic_id(
                traversal.walk_submodel(mqtt_property_collection),
                "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
            )
            if isinstance(prop_def, SubmodelElementCollection) and
            find_by_semantic_id(prop_def.value, "https://www.w3.org/2019/wot/td#hasForm") is not None
        ]
        self._topic_map = self._get_topics_from_property_definitions(property_definitions)

    def _get_topics_from_property_definitions(self, property_definitions: list[SubmodelElementCollection]) -> dict[str, str]:
        """Create a mapping of MQTT topics from the property definitions.

        :param property_definitions: The list of property definitions from the AID SM.
        :return: A dictionary mapping IdShort of MQTT topic definitions to their MQTT topic links.
        """
        topic_map: dict[str, str] = {}
        for prop_def in property_definitions:
            forms = find_by_semantic_id(
                prop_def.value, "https://www.w3.org/2019/wot/td#hasForm"
            )
            if forms is None:
                print(f"Form SMC not found in PropertyDefinition {prop_def.id_short}.")
                continue

            target_href = find_by_semantic_id(
                forms.value, "https://www.w3.org/2019/wot/hypermedia#hasTarget"
            )
            if target_href is None:
                print(f"Target property not found in Form SMC of PropertyDefinition {prop_def.id_short}.")
                continue

            topic_map[prop_def.id_short] = target_href.value
        return topic_map

    def _get_default_mqtt_interface_description(self) -> MQTTInterfaceDescription:
        """Get the default MQTT interface description from the list of MQTT interfaces.

        Default MQTT interface does not use Websocket. If no such interface is found, simply return the first one.

        :return: The default MQTT interface or None if no interface is found.
        """
        for interface in self._mqtt_interface_descriptions:
            if not interface.websocket_connection:
                print(f"Using default MQTT interface: {interface.interface_smc.id_short}")
                return interface

        if len(self._mqtt_interface_descriptions) > 0:
            print(f"Using default MQTT interface: {self._mqtt_interface_descriptions[0].interface_smc.id_short}")
            return self._mqtt_interface_descriptions[0]

        return None

    def _get_fallback_mqtt_interface_description(self) -> MQTTInterfaceDescription:
        """Get the fallback MQTT interface description from the list of MQTT interfaces.

        :return: The fallback MQTT interface or None if no second interface is provided in the AID SM.
        """
        if len(self._mqtt_interface_descriptions) > 1:
            for interface in self._mqtt_interface_descriptions:
                if interface.websocket_connection:
                    print(f"Using fallback MQTT interface: {interface.interface_smc.id_short}")
                    return interface
        return None

    def _get_mqtt_properties(self, default_mqtt_interface: SubmodelElementCollection) -> SubmodelElementCollection | None:
        """Get the MQTT properties from the InteractionMetadata SMC.

        :return: The SubmodelElementCollection containing MQTT properties on None if not found.
        """
        interaction_metadata: SubmodelElementCollection = find_by_semantic_id(
            default_mqtt_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
        )
        if interaction_metadata is None:
            print("InteractionMetadata SMC not found in MQTT interface description.")
            return None

        mqtt_property_collection: SubmodelElementCollection = find_by_semantic_id(
            interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
        )
        if mqtt_property_collection is None:
            print("PropertyAffordance SMC not found in InteractionMetadata SMC.")
            return None

        return mqtt_property_collection

    def _uses_websocket(self, mqtt_interface: SubmodelElementCollection) -> bool:
        """Check if the given MQTT interface uses a WebSocket connection by searching for the appropriate semantic ID.

        :param mqtt_interface: The MQTT interface to check.
        :return: True if the interface uses WebSocket, False otherwise.
        """
        return contains_supplemental_semantic_id(mqtt_interface, "https://www.rfc-editor.org/rfc/rfc6455")

    def get_mqtt_topic_map(self, fallback: bool = False) -> dict[str, str]:
        """Get the MQTT topic map.

        If the fallback value needs to be used, regenerate the topic map from the fallback MQTT interface.

        :param fallback: Whether to use the fallback MQTT interface, defaults to False
        :return: The MQTT topic map.
        """
        if fallback:
            self._create_topic_map(self._get_fallback().interface_smc)
        return self._topic_map

    def get_mqtt_base_url(self, fallback: bool = False) -> str:
        """Get the base URL for the MQTT connection.

        :param fallback: Whether to use the fallback MQTT interface, defaults to False
        :return: The base URL of the MQTT interface.
        """
        if fallback:
            return self._get_fallback().base_url

        return self._default_mqtt_interface.base_url

    def _get_fallback(self):
        """Get the fallback MQTT interface description if it exists.

        :raises ConnectionError: If no fallback MQTT interface is available.
        :return: The fallback MQTT interface description.
        """
        if not self._fallback_mqtt_interface:
            raise ConnectionError("No fallback MQTT interface available.")
        return self._fallback_mqtt_interface

    def uses_websocket_interface(self, fallback: bool = False) -> bool:
        """Check if the MQTT connection will be initialized using Websocket.

        :param fallback: Whether to use the fallback MQTT interface, defaults to False
        :return: True if the MQTT interface uses WebSocket, False otherwise.
        """
        if fallback:
            return self._get_fallback().websocket_connection

        return self._default_mqtt_interface.websocket_connection


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
