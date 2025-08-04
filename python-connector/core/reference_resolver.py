"""Module for resolving ReferenceElement objects to their mapped MQTT topics."""
from basyx.aas.model import ModelReference


class ReferenceResolver:
    """Static class to resolve ReferenceElement to mapped MQTT topic."""

    @staticmethod
    def get_topic_by_reference(reference: ModelReference, topic_map: dict) -> str:
        """
        Resolve a ModelReference to its mapped MQTT topic name.

        Warning: Currently the ModelReference is just a dictionary with keys and values.

        :param reference: The ModelReference to resolve.
        :param topic_map: The dictionary mapping references to topic names.
        :return: The topic name if found, else None.
        """
        # Get the last element of reference.keys if available
        last_key = reference.get("keys", [])[-1] if reference.get("keys") else None
        property_name: str = last_key["value"] if last_key else None

        if property_name and property_name in topic_map:
            return topic_map[property_name]

        return None

