from fastapi import FastAPI

from models.set_config_payload import SetConfigPayload
from models.get_value_payload import GetValuePayload
from models.response_body import ResponseBody, create_response


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Available endpoints are `/set-config` and `/get-value`"}


@app.post("/set-config")
async def set_config(payload: SetConfigPayload) -> ResponseBody:
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    json_content = payload.json_content.replace("\\\"", "\"")

    # TODO: use an AAS SDK to deserialize the content as Submodel

    # TODO: store the deserialized AID Submodel class, e.g., as global variable

    return create_response(
        status_code=200,
        message="Successfully invoked `/set-config` with raw JSON in payload",
        payload=json_content
    )


@app.post("/get-value")
async def get_value(payload: GetValuePayload) -> ResponseBody   :
    # get the raw JSON from the payload
    # the raw JSON string in the payload must escape the " character, revert this by replacing \" with "
    json_content = payload.json_content.replace("\\\"", "\"")

    # TODO: use an AAS SDK to deserialize the content as Reference

    # TODO: find the SMC in the cached AID Submodel to which the reference points

    # TODO: read the details in the SMC and use it to establish a connection to the asset

    # TODO: return the value
    result = "myResult"


    return create_response(
        status_code=200,
        message="Successfully invoked `/get-value` with raw JSON in payload",
        payload=json_content,
        value=result
    )
