import json
import threading
from typing import Dict

import uvicorn
from aas_core3.types import Submodel, Reference, SubmodelElementCollection, Property
from fastapi import FastAPI
from paho.mqtt.client import Client

from models.get_value_payload import GetValuePayload
from models.response_body import ResponseBody, create_response
from models.set_config_payload import SetConfigPayload

import aas_core3.jsonization as aas_jsonization

app = FastAPI()

mqttc: Client

base_url: str = ""

# contains the AID Submodel that is provided by set_config()
aid_sm: Submodel = None

# maps the idShort of every property in the AID SMC "properties" to
# the associated MQTT topic name "href"
topics: Dict[str, str] = {}

# maps the MQTT topic to the last received value
values: Dict[str, str] = {}


def parse_aid_topics_and_subscribe():
    global base_url

    for interface_smc_in_aid in aid_sm.over_submodel_elements_or_empty():
        # find the SMC that describes the interface e.g. "Interface_MQTT"
        if (isinstance(interface_smc_in_aid, SubmodelElementCollection) and
                interface_smc_in_aid.semantic_id.keys[0].value == "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface" and
                "mqtt" in interface_smc_in_aid.id_short.lower()):

            for metadata_in_interface_smc in interface_smc_in_aid.over_value_or_empty():
                # find the "EndpointMetadata" SMC
                if (isinstance(metadata_in_interface_smc, SubmodelElementCollection) and
                        metadata_in_interface_smc.semantic_id.keys[0].value == "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"):
                    # find the "base" Property
                    for info_in_endpointmetadata in metadata_in_interface_smc.over_value_or_empty():
                        if (isinstance(info_in_endpointmetadata, Property) and
                                info_in_endpointmetadata.semantic_id.keys[0].value == "https://www.w3.org/2019/wot/td#base"):
                            base_url = info_in_endpointmetadata.value

                # find the InteractionMetadata
                if (isinstance(metadata_in_interface_smc, SubmodelElementCollection) and
                        metadata_in_interface_smc.semantic_id.keys[0].value == "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"):
                    # find the "properties" SMC
                    for info_in_interactionmetadata in metadata_in_interface_smc.over_value_or_empty():
                        if (isinstance(info_in_interactionmetadata, SubmodelElementCollection) and
                                info_in_interactionmetadata.semantic_id.keys[0].value == "https://www.w3.org/2019/wot/td#PropertyAffordance"):
                            # find any of the sub-SMCs (one for each property)
                            # this semanticID probably matches any SMC in here, just to be sure
                            for aid_toplevel_proerty_smc in info_in_interactionmetadata.over_value_or_empty():
                                if (isinstance(aid_toplevel_proerty_smc, SubmodelElementCollection) and
                                        aid_toplevel_proerty_smc.semantic_id.keys[0].value == "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"):
                                    # you can check the idShort of aid_property_smc and you will see that this loop iterates
                                    # over all of them (axes_position, valves, status, energy)
                                    aid_property_idshort = aid_toplevel_proerty_smc.id_short
                                    print(f"Checking AID-Property: {aid_property_idshort}")

                                    # find the "forms" SMC
                                    for info_in_property_smc in aid_toplevel_proerty_smc.over_value_or_empty():
                                        if (isinstance(info_in_property_smc, SubmodelElementCollection) and
                                                info_in_property_smc.semantic_id.keys[0].value == "https://www.w3.org/2019/wot/td#hasForm"):
                                            # find the "href" Property
                                            for info_in_forms in info_in_property_smc.over_value_or_empty():
                                                if (isinstance(info_in_forms, Property) and
                                                        info_in_forms.semantic_id.keys[0].value == "https://www.w3.org/2019/wot/hypermedia#hasTarget"):
                                                    topics[aid_property_idshort] = info_in_forms.value

    mqtt_connect()


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # subscribe to all topics that we know from the AID
    for _, topic in topics.items():
        client.subscribe(topic)


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = str(msg.payload)

    print(f"Received new msg on topic {topic}")
    # cache the payload (probably JSON) for that topic
    values[topic] = payload


def mqtt_connect():
    # TODO: read the details in the SMC and use it to establish a connection to the asset
    global mqttc
    mqttc = Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    # TODO: read base address and auth from AID
    # base address is already in the form "mqtt://<host>:1883" -> mqttc.connect() only needs <host> part
    mqttc.username_pw_set(username="fluidon", password="wbEx!S!#4OHcN!5X")
    mqttc.connect("mqtt.fluidon.com", 1883, 60)

    mqttc.loop_forever()


@app.get("/")
async def root():
    return {"message": "Available endpoints are `/set-config` and `/get-value`"}


@app.post("/set-config")
async def set_config(payload: SetConfigPayload) -> ResponseBody:
    global aid_sm
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    json_content = payload.json_content.replace('\\"', '"')

    # use an AAS SDK to deserialize the content as Submodel
    # TODO: error handling - what if there is no SM
    jsonable = json.loads(json_content)
    aid_sm = aas_jsonization.submodel_from_jsonable(
        jsonable
    )

    # parse the AID and extract all topics
    # create an MQTT client and subscribe to all topics
    task = threading.Thread(target=parse_aid_topics_and_subscribe)
    task.start()

    return create_response(
        status_code=200,
        message="Successfully invoked `/set-config` with raw JSON in payload",
        payload=json_content,
    )


@app.post("/get-value")
async def get_value(payload: GetValuePayload) -> ResponseBody:
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    json_content = payload.json_content.replace('\\"', '"')

    # use an AAS SDK to deserialize the content as Reference
    jsonable = json.loads(json_content)
    prop_ref: Reference = aas_jsonization.reference_from_jsonable(jsonable)

    if prop_ref.keys[0].value != aid_sm.id:
        return create_response(status_code=404, message="Invalid AID SM-ID")

    # TODO: handle references to sub-properties
    # for now: this assumes that the provided Reference points to the top-level property
    # in the "InteractionMetadata.properties" SMC
    prop_name = prop_ref.keys[4].value

    # get the value from the cache
    topic_name = ""
    if prop_name != "" and prop_name in topics:
        topic_name = topics[prop_name]

    cached_value = ""
    if topic_name != "" and topic_name in values:
        cached_value = values[topic_name]

    result = ""
    if cached_value != "":
        result = cached_value.replace('"', '\\"').replace("\n", "")

    return create_response(
        status_code=200,
        message="Successfully invoked `/get-value` with raw JSON in payload",
        payload=json_content,
        value=result,
    )


if __name__ == "__main__":
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=8090)
