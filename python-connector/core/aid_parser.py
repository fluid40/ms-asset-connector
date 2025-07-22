"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""

from basyx.aas.model import Submodel


class AIDParser:
    """A class to handle parsing of AID Submodels and connecting to MQTT topics."""

    def __init__(self, aid_json: dict):
        """Initialize the AIDParser with a JSON representation of an AID Submodel."""
        self.aid_sm = self.parse_aid_submodel(aid_json)


    def parse_aid_and_connect(self, aid_sm: Submodel):
        """
        Parse the AID Submodel and establishes a connection to the asset via MQTT.

        :param aid_sm: The AID Submodel to parse.
        :return: Connection details or status.
        """

    def parse_aid_submodel(self, aid_json: dict) -> Submodel:
        """
        Parse the AID Submodel from a JSON representation.

        :param aid_json: The JSON representation of the AID Submodel.
        :return: An instance of the Submodel class.
        """
        # TODO find MQTT interface in submodel
        # TODO loop interaction metadata and map idShort/ key to topic links
        pass


    def _find_mqtt_interface_description(self, aid_sm: Submodel):
        """
        Find the MQTT interface description in the AID Submodel.

        :param aid_sm: The AID Submodel to search.
        :return: List of MQTT topics.
        """
        pass

    def _loop_property_definitions(self, aid_sm: Submodel):
        pass

    def _find_topics(self):
        pass