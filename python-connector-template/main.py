from fastapi import FastAPI

from models.set_config_payload import SetConfigPayload
from models.get_value_payload import GetValuePayload

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Available endpoints are `/set-config` and `/get-value`"}


@app.post("/set-config")
async def set_config(payload: SetConfigPayload):
    # get the raw JSON from the payload
    json_content = payload.json_content

    # TODO: use an AAS SDK to deserialize the content as Submodel

    # TODO: store the deserialized AID Submodel class, e.g., as global variable

    return {"message": f"Successfully set config"}


@app.get("/get-value")
async def get_value(payload: GetValuePayload):
    # get the raw JSON from the payload
    json_content = payload.json_content

    # TODO: use an AAS SDK to deserialize the content as Reference

    # TODO: find the SMC in the cached AID Submodel to which the reference points

    # TODO: read the details in the SMC and use it to establish a connection to the asset
