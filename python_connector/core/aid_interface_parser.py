"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""
import base64
from typing import Dict, List

from basyx.aas.model import (
    ExternalReference,
    Key,
    KeyTypes,
    NamespaceSet,
    Property,
    Reference,
    SubmodelElement,
    SubmodelElementCollection, ModelReference, SubmodelElementList,
)

from python_connector.core.authentication_details import IAuthenticationDetails, BasicAuthenticationDetails

from python_connector.core.authentication_details import NoAuthenticationDetails


def find_all_by_semantic_id(parent: NamespaceSet[SubmodelElement], semantic_id_value: str) -> List[SubmodelElement]:
    """Find all SubmodelElements having a specific Semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The semantic ID value to search for.
    :return: The found SubmodelElement(s) or an empty list if not found.
    """
    reference: Reference = ExternalReference(
        (Key(
            type_=KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        ),)
    )
    found_elements: list[SubmodelElement] = [
        element for element in parent if element.semantic_id.__eq__(reference)
    ]
    return found_elements


def find_by_semantic_id(parent: NamespaceSet[SubmodelElement], semantic_id_value: str) -> SubmodelElement | None:
    """Find a SubmodelElement by its semantic ID.

    :param parent: The NamespaceSet to search within.
    :param semantic_id_value: The semantic ID value to search for.
    :return: The first found SubmodelElement, or None if not found.
    """

    # create a Reference that acts like the to-be-matched semanticId
    reference: Reference = ExternalReference(
        (Key(
            type_=KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        ),)
    )

    # check if the constructed Reference appears as semanticId of the child elements
    for element in parent:
        if element.semantic_id.__eq__(reference):
            return element
    return None


def find_by_id_short(parent: NamespaceSet[SubmodelElement], id_short_value: str) -> SubmodelElement | None:
    for element in parent:
        if element.id_short == id_short_value:
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
        (Key(
            type_=KeyTypes.GLOBAL_REFERENCE,
            value=semantic_id_value
        ),)
    )
    return element.supplemental_semantic_id.__contains__(reference)


def get_base_url_from_interface(aid_interface: SubmodelElementCollection) -> str:
    """Set the base URL for the MQTT interface from the EndpointMetadata SMC."""
    endpoint_metadata: SubmodelElementCollection | None = find_by_semantic_id(
        aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
    )
    if endpoint_metadata is None:
        raise ValueError("EndpointMetadata SMC not found in AID Submodel.")

    base: Property | None = find_by_semantic_id(
        endpoint_metadata.value, "https://www.w3.org/2019/wot/td#baseURI"
    )
    if base is None:
        raise ValueError("base Property not found in EndpointMetadata SMC.")

    return base.value


def create_property_to_href_map(aid_interface: SubmodelElementCollection) -> Dict[str, Dict]:
    mapping = {}

    interaction_metadata: SubmodelElementCollection | None = find_by_semantic_id(
        aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
    )
    if interaction_metadata is None:
        raise ValueError("InteractionMetadata SMC not found in AID Submodel interface SMC.")

    properties: SubmodelElementCollection | None = find_by_semantic_id(
        interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
    )
    if properties is None:
        raise ValueError("properties SMC not found in InteractionMetadata SMC.")

    fl_properties: List[SubmodelElement] = find_all_by_semantic_id(
        properties.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/PropertyDefinition"
    )
    # TODO: some AIDs have typos in that semanticId
    fl_properties_alternative: List[SubmodelElement] = find_all_by_semantic_id(
        properties.value, "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
    )
    fl_properties.extend(fl_properties_alternative)
    if fl_properties is None:
        raise ValueError("{property} SMC not found in properties SMC.")

    def traverse_property(smc: SubmodelElementCollection, parent_path: str, href: str, key_path: List[str | int], is_items=False, idx=None, is_top_level=False):
        # determine local key only if not top-level
        if not is_top_level:
            if is_items and idx is not None:
                local_key = idx  # integer index
            else:
                key_prop = find_by_semantic_id(
                    smc.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/key"
                )
                local_key = key_prop.value if key_prop else smc.id_short  # string
            new_key_path = key_path + [local_key]
        else:
            new_key_path = key_path  # top-level: no key added

        # register this property
        full_path = f"{parent_path}.{smc.id_short}"
        mapping[full_path] = {"href": href, "keys": new_key_path}

        # traverse nested "properties" or "items"
        # (nested properties = object members, nested items = array elements)
        for nested_sem_id in [
            "https://www.w3.org/2019/wot/json-schema#properties",
            "https://www.w3.org/2019/wot/json-schema#items",
            "https://www.w3.org/2019/wot/td#PropertyAffordance"     # TODO: some apparently use this semanticId
        ]:
            nested_group: SubmodelElementCollection | None = find_by_semantic_id(smc.value, nested_sem_id)
            if nested_group:
                # attach the name of that SMC ("items" or "properties" or similar) to the key_path
                full_path += "." + nested_group.id_short

                # find all nested properties/items by semantic-ID
                nested_properties: List[SubmodelElement] = find_all_by_semantic_id(
                    nested_group.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/PropertyDefinition"
                )
                # TODO: some AIDs have typos in that semanticId
                nested_properties_alternative: List[SubmodelElement] = find_all_by_semantic_id(
                    nested_group.value, "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
                )
                nested_properties.extend(nested_properties_alternative)

                # traverse all nested properties/items recursively
                for idx, nested in enumerate(nested_properties):
                    if nested_sem_id.endswith("#items"):
                        # for arrays: append index instead of property key
                        traverse_property(nested, full_path, href, new_key_path, is_items=True, idx=idx)
                    else:
                        traverse_property(nested, full_path, href, new_key_path)

    # process all first-level properties
    for fl_property in fl_properties:
        forms: SubmodelElementCollection | None = find_by_semantic_id(
            fl_property.value, "https://www.w3.org/2019/wot/td#hasForm"
        )
        if forms is None:
            raise ValueError("forms SMC not found in {property} SMC.")

        href: Property | None = find_by_semantic_id(forms.value, "https://www.w3.org/2019/wot/hypermedia#hasTarget")
        if href is None:
            raise ValueError("href Property not found in forms SMC.")

        href_value = href.value
        idshort_path_prefix = f"{aid_interface.id_short}.{interaction_metadata.id_short}.{properties.id_short}"

        traverse_property(
            fl_property,
            idshort_path_prefix,
            href_value,
            [],
            is_top_level=True
        )

    return mapping


def construct_idshort_path_from_reference(reference: ModelReference) -> str:
    idshort_path: str = ""

    # start from the second Key and omit the Identifiable at the beginning of the list
    for key in reference.key[1:]:
        idshort_path += (key.value + ".")

    # get rid of the trailing dot
    return idshort_path[:-1]


def parse_auth(aid_interface: SubmodelElementCollection) -> IAuthenticationDetails:
    endpoint_metadata: SubmodelElementCollection | None = find_by_semantic_id(
        aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
    )
    if endpoint_metadata is None:
        raise ValueError("EndpointMetadata SMC not found in AID Submodel.")

    security: SubmodelElementList | None = find_by_semantic_id(
        endpoint_metadata.value, "https://www.w3.org/2019/wot/td#hasSecurityConfiguration"
    )
    if security is None:
        raise ValueError("security SML not found in EndpointMetadata SMC.")

    # TODO: resolve the full reference(s)
    # for now, assume there is only one reference to the security in use
    # -> access SML[0]
    # assume that this ReferenceElement points to a security scheme in this very AID SM
    # -> can just use the last key to determine the type of security
    sc = security.value[0].value.key[-1].value

    # get the securityDefinitions SMC
    security_definitions: SubmodelElementCollection | None = find_by_semantic_id(
        endpoint_metadata.value, "https://www.w3.org/2019/wot/td#definesSecurityScheme"
    )
    if security_definitions is None:
        raise ValueError("securitySchemes Property not found in EndpointMetadata SMC.")

    # find the security scheme SMC with the same idShort as mentioned in the reference "sc"
    security_details: SubmodelElementCollection | None = find_by_id_short(
        security_definitions.value, sc
    )
    if security_details is None:
        raise ValueError("Referenced security scheme SMC not found in securityDefinitions SMC")

    # get the name of the security scheme
    scheme: Property | None = find_by_semantic_id(
        security_details.value, "https://www.w3.org/2019/wot/security#SecurityScheme"
    )
    if scheme is None:
        raise ValueError("scheme Property not found in referenced security scheme SMC.")


    auth_details: IAuthenticationDetails = None

    match scheme.value:
        case "nosec":
            auth_details = NoAuthenticationDetails()

        case "basic":
            basic_sc_name: Property | None = find_by_semantic_id(
                security_details.value, "https://www.w3.org/2019/wot/security#name"
            )
            if basic_sc_name is None:
                raise ValueError("name Property not found in referenced security scheme SMC")

            auth_base64 = basic_sc_name.value
            auth_plain = base64.b64decode(auth_base64).decode("utf-8")
            auth_details = BasicAuthenticationDetails(auth_plain.split(":")[0], auth_plain.split(":")[1])

        # TODO: remaining cases

    return auth_details
